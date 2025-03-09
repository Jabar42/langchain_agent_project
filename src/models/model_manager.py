from typing import Dict, List, Optional
from langchain.schema import BaseLanguageModel
from langchain.chat_models import ChatOpenAI, ChatAnthropic, ChatCohere
from langchain.llms import OpenAI
import google.generativeai as genai
from ..utils.exceptions import ModelNotFoundError, ModelConfigError
import os
import structlog

logger = structlog.get_logger(__name__)

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
            try:
                anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
                if not anthropic_api_key:
                    logger.warning("ANTHROPIC_API_KEY not found in environment, skipping Anthropic models")
                else:
                    self.register_model(
                        "claude-2",
                        ChatAnthropic(
                            model="claude-2",
                            temperature=0.7,
                            max_tokens_to_sample=2000,
                            anthropic_api_key=anthropic_api_key
                        )
                    )
                    
                    self.register_model(
                        "claude-instant-1",
                        ChatAnthropic(
                            model="claude-instant-1",
                            temperature=0.7,
                            max_tokens_to_sample=2000,
                            anthropic_api_key=anthropic_api_key
                        )
                    )
                    logger.info("Successfully initialized Anthropic models")
            except Exception as e:
                logger.error(f"Failed to initialize Anthropic models: {str(e)}")
            
            # Cohere Models
            try:
                cohere_api_key = os.getenv("COHERE_API_KEY")
                if not cohere_api_key:
                    logger.warning("COHERE_API_KEY not found in environment, skipping Cohere models")
                else:
                    # Command model - best for instruction following
                    self.register_model(
                        "command-nightly",
                        ChatCohere(
                            model="command-nightly",
                            temperature=0.7,
                            max_tokens=2000,
                            cohere_api_key=cohere_api_key
                        )
                    )
                    
                    # Command Light model - faster, more efficient
                    self.register_model(
                        "command-light-nightly",
                        ChatCohere(
                            model="command-light-nightly",
                            temperature=0.7,
                            max_tokens=2000,
                            cohere_api_key=cohere_api_key
                        )
                    )
                    
                    # Command multilingual model
                    self.register_model(
                        "command-nightly-v2.0",
                        ChatCohere(
                            model="command-nightly-v2.0",
                            temperature=0.7,
                            max_tokens=2000,
                            cohere_api_key=cohere_api_key
                        )
                    )
                    logger.info("Successfully initialized Cohere models")
            except Exception as e:
                logger.error(f"Failed to initialize Cohere models: {str(e)}")
            
            # Google Models
            try:
                genai.configure(api_key=self._get_google_api_key())
                model = genai.GenerativeModel('gemini-pro')
                self.register_model("gemini-pro", model)
                logger.info("Successfully initialized Google models")
            except Exception as e:
                logger.error(f"Failed to initialize Google models: {str(e)}")
            
        except Exception as e:
            raise ModelConfigError(f"Error initializing default models: {str(e)}")
    
    def register_model(self, model_id: str, model: BaseLanguageModel) -> None:
        """Register a new model with the manager.
        
        Args:
            model_id: Unique identifier for the model
            model: Language model instance to register
        """
        try:
            self.models[model_id] = model
            logger.info(f"Successfully registered model: {model_id}")
        except Exception as e:
            logger.error(f"Failed to register model {model_id}: {str(e)}")
            raise ModelConfigError(f"Error registering model {model_id}: {str(e)}")
    
    def get_model(self, model_id: str) -> BaseLanguageModel:
        """Get a specific model by ID.
        
        Args:
            model_id: ID of the model to retrieve
            
        Returns:
            The requested language model
            
        Raises:
            ModelNotFoundError: If the requested model is not found
        """
        if model_id not in self.models:
            logger.error(f"Model {model_id} not found")
            raise ModelNotFoundError(f"Model {model_id} not found")
        return self.models[model_id]
    
    def get_default_models(self) -> List[str]:
        """Get list of default model IDs.
        
        Returns:
            List of default model identifiers
        """
        return self.default_models
    
    def list_available_models(self) -> List[str]:
        """List all available model IDs.
        
        Returns:
            List of all registered model identifiers
        """
        return list(self.models.keys())
    
    def remove_model(self, model_id: str) -> None:
        """Remove a model from the manager.
        
        Args:
            model_id: ID of the model to remove
        """
        if model_id in self.models:
            del self.models[model_id]
            logger.info(f"Removed model: {model_id}")
    
    def get_best_available_model(self) -> Optional[str]:
        """Get the best available model from defaults.
        
        Returns:
            ID of the best available model, or None if no default models are available
        """
        for model_id in self.default_models:
            if model_id in self.models:
                return model_id
        logger.warning("No default models available")
        return None
    
    def _get_google_api_key(self) -> str:
        """Get Google API key from environment.
        
        Returns:
            Google API key
            
        Raises:
            ModelConfigError: If API key is not found in environment
        """
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            logger.error("GOOGLE_API_KEY not found in environment")
            raise ModelConfigError("GOOGLE_API_KEY not found in environment")
        return api_key 