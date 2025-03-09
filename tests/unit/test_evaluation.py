"""Unit tests for the evaluation system."""

import pytest
from unittest.mock import Mock, AsyncMock
from src.evaluation.metrics import ResponseEvaluator
from src.evaluation.scoring import ScoreCalculator
from src.utils.exceptions import EvaluationError

@pytest.fixture
def mock_evaluator():
    evaluator = Mock(spec=ResponseEvaluator)
    evaluator.evaluate_response = AsyncMock()
    return evaluator

@pytest.fixture
def score_calculator():
    return ScoreCalculator()

@pytest.mark.asyncio
async def test_response_evaluation(mock_evaluator):
    """Test basic response evaluation."""
    test_response = "This is a test response"
    expected_response = "This is the expected response"
    
    mock_evaluator.evaluate_response.return_value = {
        "similarity_score": 0.85,
        "coherence_score": 0.9,
        "relevance_score": 0.95
    }
    
    result = await mock_evaluator.evaluate_response(test_response, expected_response)
    
    assert isinstance(result, dict)
    assert all(key in result for key in ["similarity_score", "coherence_score", "relevance_score"])
    assert all(0 <= score <= 1 for score in result.values())

def test_score_calculation(score_calculator):
    """Test score calculation with different weights."""
    metrics = {
        "similarity_score": 0.8,
        "coherence_score": 0.9,
        "relevance_score": 0.7
    }
    
    weights = {
        "similarity": 0.4,
        "coherence": 0.3,
        "relevance": 0.3
    }
    
    final_score = score_calculator.calculate_weighted_score(metrics, weights)
    assert 0 <= final_score <= 1
    
    # Test that weights sum to 1
    assert sum(weights.values()) == 1.0

@pytest.mark.asyncio
async def test_evaluation_error_handling(mock_evaluator):
    """Test error handling in evaluation."""
    mock_evaluator.evaluate_response.side_effect = EvaluationError("Invalid response format")
    
    with pytest.raises(EvaluationError):
        await mock_evaluator.evaluate_response("test", "expected")

def test_score_normalization(score_calculator):
    """Test score normalization."""
    raw_scores = {
        "metric1": 85,  # Percentage
        "metric2": 0.95,  # Already normalized
        "metric3": 4.5   # 5-point scale
    }
    
    normalized = score_calculator.normalize_scores(raw_scores)
    
    assert all(0 <= score <= 1 for score in normalized.values())
    assert abs(normalized["metric1"] - 0.85) < 0.01
    assert abs(normalized["metric2"] - 0.95) < 0.01
    assert abs(normalized["metric3"] - 0.9) < 0.01

@pytest.mark.asyncio
async def test_batch_evaluation(mock_evaluator):
    """Test evaluation of multiple responses."""
    test_responses = ["Response 1", "Response 2", "Response 3"]
    expected_responses = ["Expected 1", "Expected 2", "Expected 3"]
    
    mock_evaluator.evaluate_response.side_effect = [
        {"similarity_score": 0.8, "coherence_score": 0.9, "relevance_score": 0.7},
        {"similarity_score": 0.7, "coherence_score": 0.8, "relevance_score": 0.9},
        {"similarity_score": 0.9, "coherence_score": 0.7, "relevance_score": 0.8}
    ]
    
    results = []
    for test, expected in zip(test_responses, expected_responses):
        result = await mock_evaluator.evaluate_response(test, expected)
        results.append(result)
    
    assert len(results) == len(test_responses)
    assert all(isinstance(result, dict) for result in results)

def test_threshold_evaluation(score_calculator):
    """Test evaluation against thresholds."""
    scores = {
        "similarity_score": 0.75,
        "coherence_score": 0.85,
        "relevance_score": 0.95
    }
    
    thresholds = {
        "similarity_score": 0.7,
        "coherence_score": 0.8,
        "relevance_score": 0.9
    }
    
    meets_thresholds = score_calculator.check_thresholds(scores, thresholds)
    assert meets_thresholds is True
    
    # Test failing threshold
    thresholds["similarity_score"] = 0.8
    meets_thresholds = score_calculator.check_thresholds(scores, thresholds)
    assert meets_thresholds is False

@pytest.mark.asyncio
async def test_evaluation_metrics_range(mock_evaluator):
    """Test that evaluation metrics stay within valid ranges."""
    test_cases = [
        ("Very good response", "Expected response"),
        ("", "Expected response"),  # Edge case: empty response
        ("A" * 1000, "Expected response"),  # Edge case: very long response
    ]
    
    for test, expected in test_cases:
        mock_evaluator.evaluate_response.return_value = {
            "similarity_score": 0.5,
            "coherence_score": 0.5,
            "relevance_score": 0.5
        }
        
        result = await mock_evaluator.evaluate_response(test, expected)
        
        for metric, score in result.items():
            assert 0 <= score <= 1, f"Metric {metric} out of range [0,1]" 