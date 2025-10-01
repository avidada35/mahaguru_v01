import os
from typing import Optional

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

try:
    # Optional import; not available on many Windows/CPU setups
    from transformers.utils.quantization_config import BitsAndBytesConfig  # type: ignore
    _HAS_BNB = True
except Exception:
    BitsAndBytesConfig = None  # type: ignore
    _HAS_BNB = False

try:
    from peft import PeftModel
    _HAS_PEFT = True
except Exception:
    PeftModel = None  # type: ignore
    _HAS_PEFT = False


# === Paths & defaults ===
STUDENTGPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_MODEL = os.environ.get("STUDENTGPT_BASE_MODEL", "TinyLLaMA/TinyLLaMA-1.1B-Chat-v1.0")
ADAPTER_PATH = os.environ.get("STUDENTGPT_ADAPTER", os.path.join(STUDENTGPT_DIR, "studentgpt-lora"))

_model = None
_tokenizer = None


def _load_components():
    global _model, _tokenizer
    if _model is not None and _tokenizer is not None:
        return _model, _tokenizer

    # Load tokenizer
    tok = AutoTokenizer.from_pretrained(BASE_MODEL)
    tok.pad_token = getattr(tok, "eos_token", None) or tok.pad_token
    tok.add_special_tokens({"additional_special_tokens": ["<|im_start|>", "<|im_end|>"]})

    # Try fastest path first: 4-bit with bitsandbytes
    model: Optional[AutoModelForCausalLM] = None
    if _HAS_BNB:
        try:
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_use_double_quant=True,
            )
            model = AutoModelForCausalLM.from_pretrained(
                BASE_MODEL,
                quantization_config=bnb_config,
                device_map="auto",
                trust_remote_code=True,
            )
        except Exception:
            model = None

    # Fallback: normal FP16/FP32 on available device
    if model is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        dtype = torch.float16 if torch.cuda.is_available() else torch.float32
        model = AutoModelForCausalLM.from_pretrained(
            BASE_MODEL,
            torch_dtype=dtype,
            device_map="auto" if torch.cuda.is_available() else None,
            trust_remote_code=True,
        )
        if device == "cpu":
            model = model.to("cpu")

    # Resize embeddings for added tokens
    model.resize_token_embeddings(len(tok))

    # Optionally load LoRA adapter if present and peft available
    if _HAS_PEFT and os.path.isdir(ADAPTER_PATH):
        try:
            model = PeftModel.from_pretrained(model, ADAPTER_PATH)
        except Exception:
            # Continue without adapter
            pass

    _model, _tokenizer = model, tok
    return _model, _tokenizer


# === Chat API ===
def studentgpt_chat(query: str) -> str:
    model, tokenizer = _load_components()
    prompt = f"""<|im_start|>system
You are StudentGPT, a reflective and emotionally aware AI mentor for Indian students.
<|im_end|>
<|im_start|>user
{query}<|im_end|>
<|im_start|>assistant
"""

    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

    output = model.generate(
        **inputs,
        max_new_tokens=200,
        do_sample=True,
        temperature=0.8,
        top_p=0.9,
        eos_token_id=tokenizer.eos_token_id
    )

    decoded = tokenizer.decode(output[0], skip_special_tokens=True)
    reply = decoded.split("<|im_start|>assistant")[-1].strip()
    return reply

# === 7. Run the loop ===
if __name__ == "__main__":
    print("🧠 StudentGPT is ready. Type 'exit' to quit.")
    try:
        _load_components()
    except Exception as e:
        print(f"❌ Failed to load model: {e}")
        raise
    while True:
        q = input("👤 You: ")
        if q.lower() in ["exit", "quit"]:
            break
        print("🤖 StudentGPT:", studentgpt_chat(q))
