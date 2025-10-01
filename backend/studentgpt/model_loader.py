#!/usr/bin/env python3
"""
Model loader for StudentGPT with proper LoRA adapter integration
"""
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from transformers.utils.quantization_config import BitsAndBytesConfig
from peft import PeftModel
from pathlib import Path
import os

class StudentGPTModelLoader:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
    def load_model(self):
        """Load base model and LoRA adapter with proper path handling"""
        
        # Get absolute paths using Path.resolve() for Windows compatibility
        base_model_path = Path("./base_model").resolve()
        adapter_path = Path("./adapters").resolve()
        
        print(f"🔍 Base model path: {base_model_path}")
        print(f"🔍 Adapter path: {adapter_path}")
        
        # Verify paths exist
        if not base_model_path.exists():
            raise FileNotFoundError(f"Base model not found at {base_model_path}")
        if not adapter_path.exists():
            raise FileNotFoundError(f"Adapter not found at {adapter_path}")
            
        # Load tokenizer from base model
        print("🔤 Loading tokenizer...")
        self.tokenizer = AutoTokenizer.from_pretrained(
            base_model_path,
            local_files_only=True
        )
        
        # Add special tokens if needed
        if "<|im_start|>" not in self.tokenizer.get_vocab():
            self.tokenizer.add_special_tokens({
                "additional_special_tokens": ["<|im_start|>", "<|im_end|>"]
            })
        
        self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # Configure quantization for memory efficiency
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True
        )
        
        # Load base model
        print("🧠 Loading base model...")
        self.model = AutoModelForCausalLM.from_pretrained(
            base_model_path,
            quantization_config=bnb_config,
            device_map="auto",
            local_files_only=True
        )
        
        # Resize embeddings to match tokenizer
        self.model.resize_token_embeddings(len(self.tokenizer))
        
        # Load LoRA adapter
        print("🔧 Loading LoRA adapter...")
        self.model = PeftModel.from_pretrained(
            self.model, 
            adapter_path,
            local_files_only=True
        )
        
        print("✅ Model loaded successfully!")
        return self.model, self.tokenizer
    
    def generate_response(self, prompt, max_new_tokens=200, temperature=0.8, top_p=0.9):
        """Generate response using the loaded model"""
        if self.model is None or self.tokenizer is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        # Format prompt for StudentGPT
        formatted_prompt = f"""<|im_start|>system
You are StudentGPT, a reflective and emotionally aware AI mentor for Indian students.
<|im_end|>
<|im_start|>user
{prompt}<|im_end|>
<|im_start|>assistant
"""
        
        # Tokenize input
        inputs = self.tokenizer(formatted_prompt, return_tensors="pt")
        
        # Move to device
        if self.device == "cuda":
            inputs = {k: v.cuda() for k, v in inputs.items()}
        
        # Generate response
        with torch.no_grad():
            output = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=True,
                temperature=temperature,
                top_p=top_p,
                eos_token_id=self.tokenizer.eos_token_id,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        # Decode response
        decoded = self.tokenizer.decode(output[0], skip_special_tokens=True)
        
        # Extract assistant response
        if "<|im_start|>assistant" in decoded:
            reply = decoded.split("<|im_start|>assistant")[-1].strip()
        else:
            reply = decoded.split("assistant")[-1].strip() if "assistant" in decoded else decoded
        
        return reply

# Global model instance
model_loader = StudentGPTModelLoader()
model = None
tokenizer = None

def load_model():
    """Load the model globally"""
    global model, tokenizer
    model, tokenizer = model_loader.load_model()
    return model, tokenizer

def generate_response(prompt):
    """Generate response using the global model"""
    global model_loader
    return model_loader.generate_response(prompt) 