from typing import Dict, Any, List
from dataclasses import dataclass
from langchain.evaluation import load_evaluator
import numpy as np

@dataclass
class EvaluationCriteria:
    accuracy: float
    coherence: float
    relevance: float
    response_time: float
    token_usage: int

class ResponseEvaluator:
    """Evaluates and compares responses from different language models."""
    
    def __init__(self):
        self.criteria_weights = {
            "accuracy": 0.4,
            "coherence": 0.3,
            "relevance": 0.2,
            "response_time": 0.05,
            "token_usage": 0.05
        }
        
        # Initialize LangChain evaluators
        self.qa_evaluator = load_evaluator("qa")
        self.criteria_evaluator = load_evaluator("criteria", criteria="coherence")
        
    async def evaluate_response(
        self,
        question: str,
        response: str,
        model_id: str
    ) -> Dict[str, Any]:
        """
        Evaluate a single response based on multiple criteria.
        
        Args:
            question: Original question
            response: Model's response
            model_id: Identifier of the model used
            
        Returns:
            Dictionary containing evaluation scores
        """
        # Evaluate accuracy using QA evaluator
        qa_eval = await self.qa_evaluator.aevaluate(
            prediction=response,
            input=question
        )
        
        # Evaluate coherence
        coherence_eval = await self.criteria_evaluator.aevaluate(
            prediction=response
        )
        
        # Calculate relevance score using semantic similarity
        relevance_score = await self._calculate_relevance(question, response)
        
        evaluation = EvaluationCriteria(
            accuracy=qa_eval.score,
            coherence=coherence_eval.score,
            relevance=relevance_score,
            response_time=0.0,  # To be filled by the agent
            token_usage=0  # To be filled by the agent
        )
        
        return self._create_evaluation_dict(evaluation)
    
    async def select_best_response(
        self,
        evaluations: Dict[str, Dict[str, Any]]
    ) -> str:
        """
        Select the best response based on weighted evaluation scores.
        
        Args:
            evaluations: Dictionary of model IDs to their evaluation results
            
        Returns:
            ID of the model with the best response
        """
        scores = {}
        
        for model_id, eval_dict in evaluations.items():
            weighted_score = sum(
                eval_dict[criterion] * self.criteria_weights[criterion]
                for criterion in self.criteria_weights
            )
            scores[model_id] = weighted_score
            
        return max(scores.items(), key=lambda x: x[1])[0]
    
    async def compare_responses(
        self,
        responses: Dict[str, str],
        evaluations: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Compare responses from different models.
        
        Args:
            responses: Dictionary of model IDs to their responses
            evaluations: Dictionary of model IDs to their evaluation results
            
        Returns:
            Comparison metrics and analysis
        """
        comparison = {
            "best_model": await self.select_best_response(evaluations),
            "scores": evaluations,
            "analysis": await self._generate_comparison_analysis(responses, evaluations)
        }
        
        return comparison
    
    async def validate_response(self, response: str) -> bool:
        """
        Validate if a response meets minimum quality criteria.
        
        Args:
            response: The response to validate
            
        Returns:
            Boolean indicating if response is valid
        """
        if not response or len(response.strip()) < 10:
            return False
            
        coherence_eval = await self.criteria_evaluator.aevaluate(
            prediction=response
        )
        
        return coherence_eval.score >= 0.7
    
    async def _calculate_relevance(self, question: str, response: str) -> float:
        """Calculate semantic similarity between question and response."""
        # Implement semantic similarity calculation
        # This is a placeholder - implement with proper embedding comparison
        return 0.8
    
    def _create_evaluation_dict(self, evaluation: EvaluationCriteria) -> Dict[str, Any]:
        """Convert EvaluationCriteria to dictionary format."""
        return {
            "accuracy": evaluation.accuracy,
            "coherence": evaluation.coherence,
            "relevance": evaluation.relevance,
            "response_time": evaluation.response_time,
            "token_usage": evaluation.token_usage
        }
    
    async def _generate_comparison_analysis(
        self,
        responses: Dict[str, str],
        evaluations: Dict[str, Dict[str, Any]]
    ) -> str:
        """Generate a human-readable analysis of the comparison."""
        best_model = await self.select_best_response(evaluations)
        
        analysis = (
            f"Best performing model: {best_model}\n"
            f"Number of models compared: {len(responses)}\n"
            "Key differences:\n"
        )
        
        # Add detailed analysis of differences between responses
        # This is a placeholder - implement more sophisticated analysis
        
        return analysis 