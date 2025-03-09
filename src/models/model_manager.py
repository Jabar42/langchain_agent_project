from typing import Dict, List, Optional
from langchain.schema import BaseLanguageModel
from langchain.chat_models import ChatOpenAI, ChatAnthropic, ChatCohere
from langchain.llms import OpenAI
import google.generativeai as genai
from ..utils.exceptions import ModelNotFoundError, ModelConfigError

class ModelManager:
    """Manages multiple language models and their configurations."""
    
    def __init__(self):
        self.models: Dict[str, BaseLanguageModel] = {}
        self.default_models = ["gpt-4", "claude-2", "command-nightly"]
        self._initialize_default_models()
    
    def _initialize_default_models(self):
        """Initialize default models based on environment configuration."""
        try:
            # OpenAI Models
            self.register_model(
                "gpt-4",
                ChatOpenAI(
                    model_name="gpt-4",
                    temperature=0.7,
                    max_tokens=2000
                )
            )
            
            self.register_model(
                "gpt-3.5-turbo",
                ChatOpenAI(
                    model_name="gpt-3.5-turbo",
                    temperature=0.7,
                    max_tokens=2000
                )
            )
            
            # Anthropic Models
            self.register_model(
                "claude-2",
                ChatAnthropic(
                    model="claude-2",
                    temperature=0.7,
                    max_tokens_to_sample=2000
                )
            )
            
            # Cohere Models
            self.register_model(
                "command-nightly",
                ChatCohere(
                    model="command-nightly",
                    temperature=0.7,
                    max_tokens=2000
                )
            )
            
            # Google Models
            genai.configure(api_key=self._get_google_api_key())
            model = genai.GenerativeModel('gemini-pro')
            self.register_model("gemini-pro", model)
            
        except Exception as e:
            raise ModelConfigError(f"Error initializing default models: {str(e)}")
    
    def register_model(self, model_id: str, model: BaseLanguageModel) -> None:
        """Register a new model with the manager."""
        self.models[model_id] = model
    
    def get_model(self, model_id: str) -> BaseLanguageModel:
        """Get a specific model by ID."""
        if model_id not in self.models:
            raise ModelNotFoundError(f"Model {model_id} not found")
        return self.models[model_id]
    
    def get_default_models(self) -> List[str]:
        """Get list of default model IDs."""
        return self.default_models
    
    def list_available_models(self) -> List[str]:
        """List all available model IDs."""
        return list(self.models.keys())
    
    def remove_model(self, model_id: str) -> None:
        """Remove a model from the manager."""
        if model_id in self.models:
            del self.models[model_id]
    
    def get_best_available_model(self) -> Optional[str]:
        """Get the best available model from defaults."""
        for model_id in self.default_models:
            if model_id in self.models:
                return model_id
        return None
    
    def _get_google_api_key(self) -> str:
        """Get Google API key from environment."""
        import os
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ModelConfigError("GOOGLE_API_KEY not found in environment")
        return api_key 