from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import torch
import os

# Model paths
base_model_path = "TinyLLaMA/TinyLLaMA-1.1B-Chat-v1.0"
adapter_path = os.path.join(os.path.dirname(__file__), "studentgpt-lora")

# Global variables for model and tokenizer
tokenizer = None
model = None

def load_model():
    """Load the model and tokenizer"""
    global tokenizer, model
    
    if tokenizer is None or model is None:
        print(f"Loading base model: {base_model_path}")
        print(f"Loading LoRA adapter from: {adapter_path}")
        
        # Load tokenizer from adapter path (should have the same tokenizer)
        tokenizer = AutoTokenizer.from_pretrained(adapter_path)
        
        # Load base model
        base_model = AutoModelForCausalLM.from_pretrained(
            base_model_path,
            torch_dtype=torch.float16,
            low_cpu_mem_usage=True,
            device_map="auto"
        )
        
        # Load LoRA adapter
        model = PeftModel.from_pretrained(base_model, adapter_path)
        
        print("✅ Model loaded successfully")

def format_chat_history(history):
    """Format chat history into a prompt string"""
    formatted_prompt = ""
    for message in history:
        role = message.get("role", "student")
        content = message.get("content", "")
        
        if role == "student":
            formatted_prompt += f"Student: {content}\n"
        elif role == "mentor":
            formatted_prompt += f"Mentor: {content}\n"
    
    # Add the mentor prefix for the response
    formatted_prompt += "Mentor: "
    return formatted_prompt

def generate_response(history):
    """Generate a response based on chat history"""
    # Load model if not already loaded
    if tokenizer is None or model is None:
        load_model()
    
    # Format the chat history into a prompt
    prompt = format_chat_history(history)
    
    # Tokenize the input
    inputs = tokenizer(prompt, return_tensors="pt")
    
    # Generate response
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=200,
            temperature=0.7,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )
    
    # Decode the response
    full_response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # Extract only the new generated text (remove the input prompt)
    response = full_response[len(prompt):].strip()
    
    return response

# Load model on module import
try:
    load_model()
except Exception as e:
    print(f"⚠️ Warning: Could not load model on startup: {e}")
    print("Model will be loaded when first used.") 