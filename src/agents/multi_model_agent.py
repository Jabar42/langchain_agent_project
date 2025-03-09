from typing import List, Dict, Any
from .base_agent import BaseAgent
from ..models.model_manager import ModelManager
from ..evaluators.response_evaluator import ResponseEvaluator
from langchain.schema import BaseLanguageModel

class MultiModelAgent(BaseAgent):
    """Agent capable of handling multiple language models and comparing their responses."""
    
    def __init__(self, default_llm: BaseLanguageModel):
        super().__init__(default_llm)
        self.model_manager = ModelManager()
        self.evaluator = ResponseEvaluator()
        
    async def process_message(self, message: str, models: List[str] = None) -> Dict[str, Any]:
        """
        Process a message using multiple models and return their responses with evaluations.
        
        Args:
            message: The input message to process
            models: List of model identifiers to use. If None, uses default models.
            
        Returns:
            Dictionary containing responses and their evaluations
        """
        if not models:
            models = self.model_manager.get_default_models()
            
        responses = {}
        evaluations = {}
        
        # Get responses from all specified models
        for model_id in models:
            try:
                model = self.model_manager.get_model(model_id)
                response = await self._get_model_response(model, message)
                responses[model_id] = response
                
                # Evaluate each response
                evaluation = await self.evaluator.evaluate_response(
                    message,
                    response,
                    model_id
                )
                evaluations[model_id] = evaluation
                
            except Exception as e:
                await self.handle_error(e)
                
        # Select best response based on evaluations
        best_response = await self.evaluator.select_best_response(evaluations)
        
        result = {
            "responses": responses,
            "evaluations": evaluations,
            "best_response": best_response
        }
        
        self.add_to_history(message, result)
        return result
    
    async def handle_error(self, error: Exception) -> str:
        """Handle errors during multi-model processing."""
        error_message = f"Error during multi-model processing: {str(error)}"
        # Log error for monitoring
        return error_message
    
    async def validate_response(self, response: str) -> bool:
        """Validate a response using the evaluator."""
        return await self.evaluator.validate_response(response)
    
    async def _get_model_response(self, model: BaseLanguageModel, message: str) -> str:
        """Get response from a specific model."""
        try:
            response = await model.agenerate([message])
            return response.generations[0][0].text
        except Exception as e:
            raise Exception(f"Error getting response from model: {str(e)}")
            
    async def compare_responses(self, message: str, models: List[str]) -> Dict[str, Any]:
        """
        Compare responses from different models for the same input.
        
        Args:
            message: Input message to compare responses for
            models: List of model identifiers to compare
            
        Returns:
            Comparison results including responses and evaluations
        """
        result = await self.process_message(message, models)
        
        # Add comparison metrics
        comparison = await self.evaluator.compare_responses(
            result["responses"],
            result["evaluations"]
        )
        
        result["comparison"] = comparison
        return result 