import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StudentGPT:
    def __init__(self, model_name="TinyLlama/TinyLlama-1.1B-Chat-v1.0"):
        """
        Initialize the StudentGPT model with TinyLlama 1.1B
        
        Args:
            model_name (str): The model name/path for the fine-tuned TinyLlama model
        """
        self.model_name = model_name
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.session_history = {}  # Dictionary to store session-based conversation history
        
        logger.info(f"Loading model: {model_name}")
        logger.info(f"Using device: {self.device}")
        
        # Load tokenizer and model
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map="auto" if torch.cuda.is_available() else None
            )
            
            # Set pad token if not exists
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
                
            logger.info("Model loaded successfully!")
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise e
    
    def _format_conversation_history(self, session_id):
        """
        Format the conversation history for a given session
        
        Args:
            session_id (str): The session identifier
            
        Returns:
            str: Formatted conversation history
        """
        if session_id not in self.session_history:
            return ""
        
        history = self.session_history[session_id]
        formatted_history = ""
        
        for exchange in history:
            formatted_history += f"User: {exchange['user']}\nAssistant: {exchange['assistant']}\n"
        
        return formatted_history
    
    def generate_response(self, session_id, user_input, max_length=512, temperature=0.7, do_sample=True):
        """
        Generate a response for the given user input and session
        
        Args:
            session_id (str): The session identifier
            user_input (str): The user's input message
            max_length (int): Maximum length of generated response
            temperature (float): Sampling temperature for generation
            do_sample (bool): Whether to use sampling for generation
            
        Returns:
            str: The generated response
        """
        try:
            # Get conversation history for this session
            conversation_history = self._format_conversation_history(session_id)
            
            # Create the prompt with history and new input
            if conversation_history:
                prompt = f"{conversation_history}User: {user_input}\nAssistant:"
            else:
                prompt = f"User: {user_input}\nAssistant:"
            
            # Tokenize the input
            inputs = self.tokenizer.encode(prompt, return_tensors="pt").to(self.device)
            
            # Generate response
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    max_length=min(inputs.shape[1] + max_length, 1024),  # Limit total length
                    temperature=temperature,
                    do_sample=do_sample,
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                    num_return_sequences=1
                )
            
            # Decode the response
            full_response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract only the assistant's response (everything after the last "Assistant:")
            if "Assistant:" in full_response:
                assistant_response = full_response.split("Assistant:")[-1].strip()
            else:
                assistant_response = full_response[len(prompt):].strip()
            
            # Clean up the response
            assistant_response = assistant_response.split("User:")[0].strip()  # Remove any trailing user input
            
            # Store the conversation in session history
            if session_id not in self.session_history:
                self.session_history[session_id] = []
            
            self.session_history[session_id].append({
                "user": user_input,
                "assistant": assistant_response
            })
            
            # Keep only last 10 exchanges to prevent context from growing too large
            if len(self.session_history[session_id]) > 10:
                self.session_history[session_id] = self.session_history[session_id][-10:]
            
            logger.info(f"Generated response for session {session_id}")
            return assistant_response
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "I'm sorry, I encountered an error while processing your request. Please try again."
    
    def clear_session(self, session_id):
        """
        Clear the conversation history for a specific session
        
        Args:
            session_id (str): The session identifier to clear
        """
        if session_id in self.session_history:
            del self.session_history[session_id]
            logger.info(f"Cleared session history for {session_id}")
    
    def get_session_history(self, session_id):
        """
        Get the conversation history for a specific session
        
        Args:
            session_id (str): The session identifier
            
        Returns:
            list: List of conversation exchanges
        """
        return self.session_history.get(session_id, [])
