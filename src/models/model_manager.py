from typing import Dict, List, Optional, Tuple
from langchain.schema import BaseLanguageModel
from langchain.chat_models import ChatOpenAI, ChatAnthropic, ChatCohere
from langchain.llms import OpenAI
import google.generativeai as genai
from ..utils.exceptions import ModelNotFoundError, ModelConfigError
import os
import structlog
from dataclasses import dataclass
from .model_tier import ModelTier

logger = structlog.get_logger(__name__)

@dataclass
class ModelInfo:
    """Stores information about a model."""
    model: BaseLanguageModel
    tier: ModelTier
    is_available: bool = True
    error_count: int = 0
    max_errors: int = 3

class ModelManager:
    """Manages multiple language models and their configurations."""
    
    def __init__(self):
        self.models: Dict[str, ModelInfo] = {}
        self.default_models = ["gpt-4", "claude-2", "command-nightly"]
        self.fallback_chains = {
            ModelTier.PREMIUM: ["gpt-4", "claude-2", "gemini-ultra"],
            ModelTier.ADVANCED: ["gpt-3.5-turbo", "claude-instant-1", "command-nightly"],
            ModelTier.STANDARD: ["command-light-nightly", "gemini-pro"],
            ModelTier.BASIC: ["command-nightly-v2.0"]
        }
        self._initialize_default_models()
    
    def _initialize_default_models(self):
        """Initialize default models based on environment configuration."""
        try:
            # OpenAI Models
            self._init_openai_models()
            
            # Anthropic Models
            self._init_anthropic_models()
            
            # Cohere Models
            self._init_cohere_models()
            
            # Google Models
            self._init_google_models()
            
        except Exception as e:
            raise ModelConfigError(f"Error initializing default models: {str(e)}")
    
    def _init_openai_models(self):
        """Initialize OpenAI models."""
        try:
            self.register_model(
                "gpt-4",
                ChatOpenAI(
                    model_name="gpt-4",
                    temperature=0.7,
                    max_tokens=2000
                ),
                ModelTier.PREMIUM
            )
            
            self.register_model(
                "gpt-3.5-turbo",
                ChatOpenAI(
                    model_name="gpt-3.5-turbo",
                    temperature=0.7,
                    max_tokens=2000
                ),
                ModelTier.ADVANCED
            )
            logger.info("Successfully initialized OpenAI models")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI models: {str(e)}")
    
    def _init_anthropic_models(self):
        """Initialize Anthropic models."""
        try:
            anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
            if not anthropic_api_key:
                logger.warning("ANTHROPIC_API_KEY not found in environment, skipping Anthropic models")
                return
            
            self.register_model(
                "claude-2",
                ChatAnthropic(
                    model="claude-2",
                    temperature=0.7,
                    max_tokens_to_sample=2000,
                    anthropic_api_key=anthropic_api_key
                ),
                ModelTier.PREMIUM
            )
            
            self.register_model(
                "claude-instant-1",
                ChatAnthropic(
                    model="claude-instant-1",
                    temperature=0.7,
                    max_tokens_to_sample=2000,
                    anthropic_api_key=anthropic_api_key
                ),
                ModelTier.ADVANCED
            )
            logger.info("Successfully initialized Anthropic models")
        except Exception as e:
            logger.error(f"Failed to initialize Anthropic models: {str(e)}")
    
    def _init_cohere_models(self):
        """Initialize Cohere models."""
        try:
            cohere_api_key = os.getenv("COHERE_API_KEY")
            if not cohere_api_key:
                logger.warning("COHERE_API_KEY not found in environment, skipping Cohere models")
                return
            
            self.register_model(
                "command-nightly",
                ChatCohere(
                    model="command-nightly",
                    temperature=0.7,
                    max_tokens=2000,
                    cohere_api_key=cohere_api_key
                ),
                ModelTier.ADVANCED
            )
            
            self.register_model(
                "command-light-nightly",
                ChatCohere(
                    model="command-light-nightly",
                    temperature=0.7,
                    max_tokens=2000,
                    cohere_api_key=cohere_api_key
                ),
                ModelTier.STANDARD
            )
            
            self.register_model(
                "command-nightly-v2.0",
                ChatCohere(
                    model="command-nightly-v2.0",
                    temperature=0.7,
                    max_tokens=2000,
                    cohere_api_key=cohere_api_key
                ),
                ModelTier.BASIC
            )
            logger.info("Successfully initialized Cohere models")
        except Exception as e:
            logger.error(f"Failed to initialize Cohere models: {str(e)}")
    
    def _init_google_models(self):
        """Initialize Google models."""
        try:
            google_api_key = self._get_google_api_key()
            genai.configure(api_key=google_api_key)
            
            self.register_model(
                "gemini-pro",
                genai.GenerativeModel(
                    'gemini-pro',
                    generation_config={
                        'temperature': 0.7,
                        'top_p': 0.95,
                        'top_k': 40,
                        'max_output_tokens': 2048,
                    }
                ),
                ModelTier.STANDARD
            )
            
            self.register_model(
                "gemini-pro-vision",
                genai.GenerativeModel(
                    'gemini-pro-vision',
                    generation_config={
                        'temperature': 0.7,
                        'top_p': 0.95,
                        'top_k': 40,
                        'max_output_tokens': 2048,
                    }
                ),
                ModelTier.ADVANCED
            )
            
            try:
                self.register_model(
                    "gemini-ultra",
                    genai.GenerativeModel(
                        'gemini-ultra',
                        generation_config={
                            'temperature': 0.7,
                            'top_p': 0.95,
                            'top_k': 40,
                            'max_output_tokens': 8192,
                        }
                    ),
                    ModelTier.PREMIUM
                )
            except Exception as e:
                logger.warning(f"Gemini Ultra model not available: {str(e)}")
            
            logger.info("Successfully initialized Google models")
        except Exception as e:
            logger.error(f"Failed to initialize Google models: {str(e)}")
    
    def register_model(self, model_id: str, model: BaseLanguageModel, tier: ModelTier) -> None:
        """Register a new model with the manager.
        
        Args:
            model_id: Unique identifier for the model
            model: Language model instance to register
            tier: The capability tier of the model
        """
        try:
            self.models[model_id] = ModelInfo(model=model, tier=tier)
            logger.info(f"Successfully registered model: {model_id}")
        except Exception as e:
            logger.error(f"Failed to register model {model_id}: {str(e)}")
            raise ModelConfigError(f"Error registering model {model_id}: {str(e)}")
    
    def get_model(self, model_id: str, use_fallback: bool = True) -> Tuple[str, BaseLanguageModel]:
        """Get a specific model by ID with fallback support.
        
        Args:
            model_id: ID of the model to retrieve
            use_fallback: Whether to use fallback models if the requested model is unavailable
            
        Returns:
            A tuple of (model_id, model) where model_id might be different from the requested one if fallback was used
            
        Raises:
            ModelNotFoundError: If the requested model and no fallback models are available
        """
        if model_id not in self.models:
            if not use_fallback:
                logger.error(f"Model {model_id} not found")
                raise ModelNotFoundError(f"Model {model_id} not found")
            return self._get_fallback_model(model_id)
        
        model_info = self.models[model_id]
        if not model_info.is_available:
            if not use_fallback:
                logger.error(f"Model {model_id} is currently unavailable")
                raise ModelNotFoundError(f"Model {model_id} is currently unavailable")
            return self._get_fallback_model(model_id)
        
        return model_id, model_info.model
    
    def _get_fallback_model(self, original_model_id: str) -> Tuple[str, BaseLanguageModel]:
        """Get a fallback model when the requested model is unavailable.
        
        Args:
            original_model_id: ID of the originally requested model
            
        Returns:
            A tuple of (model_id, model) for the fallback model
            
        Raises:
            ModelNotFoundError: If no fallback models are available
        """
        if original_model_id not in self.models:
            logger.warning(f"Model {original_model_id} not found, using best available model")
            return self._get_best_available_model()
        
        original_tier = self.models[original_model_id].tier
        
        # Try models in the same tier first
        for model_id in self.fallback_chains[original_tier]:
            if model_id in self.models and self.models[model_id].is_available:
                logger.info(f"Using fallback model {model_id} for {original_model_id}")
                return model_id, self.models[model_id].model
        
        # Try models in lower tiers
        current_tier = original_tier
        while current_tier != ModelTier.BASIC:
            current_tier = ModelTier(current_tier.value - 1)
            for model_id in self.fallback_chains[current_tier]:
                if model_id in self.models and self.models[model_id].is_available:
                    logger.info(f"Using lower tier fallback model {model_id} for {original_model_id}")
                    return model_id, self.models[model_id].model
        
        logger.error("No fallback models available")
        raise ModelNotFoundError("No fallback models available")
    
    def _get_best_available_model(self) -> Tuple[str, BaseLanguageModel]:
        """Get the best available model from any tier.
        
        Returns:
            A tuple of (model_id, model) for the best available model
            
        Raises:
            ModelNotFoundError: If no models are available
        """
        for tier in reversed(list(ModelTier)):
            for model_id in self.fallback_chains[tier]:
                if model_id in self.models and self.models[model_id].is_available:
                    logger.info(f"Selected best available model: {model_id}")
                    return model_id, self.models[model_id].model
        
        logger.error("No models available")
        raise ModelNotFoundError("No models available")
    
    def mark_model_error(self, model_id: str) -> None:
        """Mark a model as having encountered an error.
        
        Args:
            model_id: ID of the model that encountered an error
        """
        if model_id in self.models:
            model_info = self.models[model_id]
            model_info.error_count += 1
            if model_info.error_count >= model_info.max_errors:
                model_info.is_available = False
                logger.warning(f"Model {model_id} marked as unavailable due to too many errors")
    
    def reset_model_status(self, model_id: str) -> None:
        """Reset the error count and availability status of a model.
        
        Args:
            model_id: ID of the model to reset
        """
        if model_id in self.models:
            model_info = self.models[model_id]
            model_info.error_count = 0
            model_info.is_available = True
            logger.info(f"Reset status for model {model_id}")
    
    def get_model_tier(self, model_id: str) -> Optional[ModelTier]:
        """Get the tier of a specific model.
        
        Args:
            model_id: ID of the model
            
        Returns:
            The model's tier or None if the model is not found
        """
        return self.models[model_id].tier if model_id in self.models else None
    
    def list_available_models(self, tier: Optional[ModelTier] = None) -> List[str]:
        """List all available model IDs, optionally filtered by tier.
        
        Args:
            tier: Optional tier to filter models by
            
        Returns:
            List of available model identifiers
        """
        if tier is None:
            return [model_id for model_id, info in self.models.items() if info.is_available]
        return [model_id for model_id, info in self.models.items() 
                if info.is_available and info.tier == tier]
    
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