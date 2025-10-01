import torch
from transformers import AutoTokenizer, TrainingArguments, BitsAndBytesConfig, AutoModelForCausalLM
from trl import SFTTrainer
from datasets import load_dataset
from peft import LoraConfig, get_peft_model

# === 1. Configs ===
MODEL_NAME = "TinyLLaMA/TinyLLaMA-1.1B-Chat-v1.0"

# === 2. Load dataset ===
dataset = load_dataset("json", data_files="formatted_studentgpt_dataset.jsonl", split="train")
print("🧪 Sample input for training:\n")
print(dataset[0]["text"][:500])

# === 3. Load tokenizer ===
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
tokenizer.pad_token = tokenizer.eos_token

# === 4. Add ChatML tokens if needed ===
special_tokens_dict = {
    "additional_special_tokens": ["<|im_start|>", "<|im_end|>"]
}
tokenizer.add_special_tokens(special_tokens_dict)

# === 5. Load model in 4-bit with QLoRA ===
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_quant_type="nf4"
)

model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    quantization_config=bnb_config,
    device_map="auto"
)
model.resize_token_embeddings(len(tokenizer))  # Expand for ChatML tokens

# === 6. Inject LoRA Adapters ===
peft_config = LoraConfig(
    r=8,
    lora_alpha=16,
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
    target_modules=["q_proj", "v_proj"]
)

from peft import prepare_model_for_kbit_training
model = prepare_model_for_kbit_training(model)
model = get_peft_model(model, peft_config)

model.train()

# === 7. Print trainable params ===
def print_trainable_params(model):
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total = sum(p.numel() for p in model.parameters())
    print(f"✅ Trainable params: {trainable:,} / {total:,} ({100 * trainable / total:.4f}%)")
print_trainable_params(model)

# === 8. Tokenize function ===
def tokenize_chat(batch):
    encoded = tokenizer(
        batch["text"],
        truncation=True,
        padding="max_length",
        max_length=1024,
        return_attention_mask=True
    )
    return {
        "input_ids": encoded["input_ids"],
        "attention_mask": encoded["attention_mask"],
        "labels": encoded["input_ids"]  # For causal LM
    }

tokenized_dataset = dataset.map(tokenize_chat, batched=True)

# === 9. Debug a sample before training ===
print("\n🔍 Debug tokenized sample keys:", tokenized_dataset[0].keys())

try:
    sample = tokenized_dataset[0]
    inputs = {
        "input_ids": torch.tensor([sample["input_ids"]]).to(model.device),
        "attention_mask": torch.tensor([sample["attention_mask"]]).to(model.device),
        "labels": torch.tensor([sample["labels"]]).to(model.device)
    }
    with torch.no_grad():
        out = model(**inputs)
        print("✅ Sample loss check passed:", out.loss.item())
except Exception as e:
    print("❌ Sample forward pass failed:", str(e))
    exit()

# === 10. Training arguments ===
training_args = TrainingArguments(
    output_dir="./studentgpt-lora",
    num_train_epochs=20,
    per_device_train_batch_size=1,
    gradient_accumulation_steps=4,
    gradient_checkpointing=True,
    learning_rate=3e-4,
    logging_steps=5,
    save_steps=50,
    save_total_limit=1,
    bf16=False,
    fp16=True,
    optim="paged_adamw_8bit",
    lr_scheduler_type="cosine",
    warmup_steps=5,
    logging_dir="./logs",
    report_to="none"
)

# === 11. Launch trainer ===
trainer = SFTTrainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
    peft_config=peft_config
)

trainer.train()

# === 12. Save LoRA adapter ===
trainer.model.save_pretrained("studentgpt-lora")
tokenizer.save_pretrained("studentgpt-lora")

print("✅ Fine-tuning complete. LoRA adapter saved to ./studentgpt-lora")
