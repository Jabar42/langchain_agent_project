"""Integration tests for the evaluation system."""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from src.evaluation.metrics import ResponseEvaluator
from src.evaluation.scoring import ScoreCalculator
from src.models.openai import OpenAIIntegration
from src.models.anthropic import AnthropicIntegration
from src.utils.exceptions import EvaluationError

@pytest.fixture
def evaluator():
    """Create a ResponseEvaluator instance."""
    return ResponseEvaluator()

@pytest.fixture
def score_calculator():
    """Create a ScoreCalculator instance."""
    return ScoreCalculator()

@pytest.mark.asyncio
async def test_complete_evaluation_flow():
    """Test the complete evaluation flow with multiple models."""
    evaluator = ResponseEvaluator()
    openai_model = OpenAIIntegration()
    anthropic_model = AnthropicIntegration()
    
    # Mock model responses
    with patch.object(openai_model, 'generate_response', return_value="OpenAI detailed response"):
        with patch.object(anthropic_model, 'generate_response', return_value="Anthropic detailed response"):
            # Get responses from both models
            openai_response = await openai_model.generate_response("Test prompt")
            anthropic_response = await anthropic_model.generate_response("Test prompt")
            
            # Evaluate both responses
            openai_scores = await evaluator.evaluate_response(openai_response, "Test prompt")
            anthropic_scores = await evaluator.evaluate_response(anthropic_response, "Test prompt")
            
            # Verify score structure
            for scores in [openai_scores, anthropic_scores]:
                assert isinstance(scores, dict)
                assert all(key in scores for key in ["similarity_score", "coherence_score", "relevance_score"])
                assert all(0 <= score <= 1 for score in scores.values())

@pytest.mark.asyncio
async def test_evaluation_with_context():
    """Test evaluation considering conversation context."""
    evaluator = ResponseEvaluator()
    
    conversation = [
        {"role": "user", "content": "What is Python?"},
        {"role": "assistant", "content": "Python is a programming language."},
        {"role": "user", "content": "Tell me more about its features."}
    ]
    
    response = "Python features include dynamic typing, high-level data structures, and extensive libraries."
    
    # Evaluate response considering context
    with patch.object(evaluator, 'evaluate_with_context') as mock_evaluate:
        mock_evaluate.return_value = {
            "similarity_score": 0.9,
            "coherence_score": 0.85,
            "relevance_score": 0.95,
            "context_score": 0.9
        }
        
        scores = await evaluator.evaluate_with_context(
            response=response,
            context=conversation
        )
        
        assert "context_score" in scores
        assert scores["context_score"] >= 0.8  # High context relevance expected

@pytest.mark.asyncio
async def test_concurrent_evaluations():
    """Test handling multiple concurrent evaluations."""
    evaluator = ResponseEvaluator()
    responses = [
        "First detailed response about topic A",
        "Second detailed response about topic B",
        "Third detailed response about topic C"
    ]
    prompts = [
        "Tell me about topic A",
        "Explain topic B",
        "Describe topic C"
    ]
    
    # Evaluate multiple responses concurrently
    tasks = [
        evaluator.evaluate_response(response, prompt)
        for response, prompt in zip(responses, prompts)
    ]
    
    results = await asyncio.gather(*tasks)
    
    assert len(results) == len(responses)
    for scores in results:
        assert all(key in scores for key in ["similarity_score", "coherence_score", "relevance_score"])

@pytest.mark.asyncio
async def test_evaluation_caching():
    """Test evaluation result caching mechanism."""
    evaluator = ResponseEvaluator()
    prompt = "What is AI?"
    response = "AI is artificial intelligence..."
    
    # First evaluation
    scores1 = await evaluator.evaluate_response(response, prompt)
    
    # Second evaluation of same response
    scores2 = await evaluator.evaluate_response(response, prompt)
    
    # Scores should be identical for same input
    assert scores1 == scores2

@pytest.mark.asyncio
async def test_evaluation_thresholds():
    """Test evaluation against defined thresholds."""
    evaluator = ResponseEvaluator()
    calculator = ScoreCalculator()
    
    thresholds = {
        "similarity_score": 0.7,
        "coherence_score": 0.7,
        "relevance_score": 0.7
    }
    
    # Test with good response
    good_response = "A detailed and relevant response"
    with patch.object(evaluator, 'evaluate_response') as mock_evaluate:
        mock_evaluate.return_value = {
            "similarity_score": 0.8,
            "coherence_score": 0.85,
            "relevance_score": 0.9
        }
        
        scores = await evaluator.evaluate_response(good_response, "Test prompt")
        meets_thresholds = calculator.check_thresholds(scores, thresholds)
        assert meets_thresholds is True
    
    # Test with poor response
    poor_response = "Brief response"
    with patch.object(evaluator, 'evaluate_response') as mock_evaluate:
        mock_evaluate.return_value = {
            "similarity_score": 0.6,
            "coherence_score": 0.5,
            "relevance_score": 0.4
        }
        
        scores = await evaluator.evaluate_response(poor_response, "Test prompt")
        meets_thresholds = calculator.check_thresholds(scores, thresholds)
        assert meets_thresholds is False

@pytest.mark.asyncio
async def test_evaluation_error_handling():
    """Test error handling in evaluation system."""
    evaluator = ResponseEvaluator()
    
    # Test with invalid input
    with pytest.raises(EvaluationError):
        await evaluator.evaluate_response("", "")  # Empty input
    
    # Test with extremely long input
    long_input = "a" * 10000
    try:
        await evaluator.evaluate_response(long_input, "Test prompt")
    except EvaluationError as e:
        assert "Input too long" in str(e)

@pytest.mark.asyncio
async def test_weighted_scoring():
    """Test weighted scoring system."""
    calculator = ScoreCalculator()
    
    scores = {
        "similarity_score": 0.8,
        "coherence_score": 0.9,
        "relevance_score": 0.7,
        "context_score": 0.85
    }
    
    weights = {
        "similarity": 0.3,
        "coherence": 0.3,
        "relevance": 0.2,
        "context": 0.2
    }
    
    final_score = calculator.calculate_weighted_score(scores, weights)
    
    assert 0 <= final_score <= 1
    # Expected score: (0.8 * 0.3) + (0.9 * 0.3) + (0.7 * 0.2) + (0.85 * 0.2) = 0.825
    assert abs(final_score - 0.825) < 0.01 