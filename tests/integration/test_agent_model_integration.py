"""Integration tests for Agent-Model interaction."""

import pytest
import asyncio
from src.agents.multi_model_agent import MultiModelAgent
from src.models.openai import OpenAIIntegration
from src.models.anthropic import AnthropicIntegration
from src.evaluation.metrics import ResponseEvaluator
from src.utils.exceptions import ModelError
from unittest.mock import AsyncMock, patch

@pytest.fixture
async def multi_model_agent():
    """Create a MultiModelAgent instance with multiple models."""
    openai_model = OpenAIIntegration()
    anthropic_model = AnthropicIntegration()
    evaluator = ResponseEvaluator()
    
    agent = MultiModelAgent(
        primary_model=openai_model,
        fallback_models=[anthropic_model],
        evaluator=evaluator
    )
    return agent

@pytest.mark.asyncio
async def test_model_fallback_flow():
    """Test the complete fallback flow when primary model fails."""
    openai_model = OpenAIIntegration()
    anthropic_model = AnthropicIntegration()
    evaluator = ResponseEvaluator()
    
    # Mock OpenAI to fail
    with patch.object(openai_model, 'generate_response', side_effect=ModelError("API Error")):
        # Mock Anthropic to succeed
        with patch.object(anthropic_model, 'generate_response', return_value="Fallback response"):
            agent = MultiModelAgent(
                primary_model=openai_model,
                fallback_models=[anthropic_model],
                evaluator=evaluator
            )
            
            response = await agent.process_message("Test message")
            assert "Fallback response" in response
            assert agent.current_model == anthropic_model

@pytest.mark.asyncio
async def test_model_evaluation_flow():
    """Test the evaluation flow between multiple models."""
    openai_model = OpenAIIntegration()
    anthropic_model = AnthropicIntegration()
    evaluator = ResponseEvaluator()
    
    # Mock responses
    with patch.object(openai_model, 'generate_response', return_value="OpenAI response"):
        with patch.object(anthropic_model, 'generate_response', return_value="Anthropic response"):
            with patch.object(evaluator, 'evaluate_response') as mock_evaluate:
                # Configure evaluator to prefer Anthropic's response
                mock_evaluate.side_effect = [
                    {"similarity_score": 0.7, "coherence_score": 0.7, "relevance_score": 0.7},  # OpenAI
                    {"similarity_score": 0.9, "coherence_score": 0.9, "relevance_score": 0.9}   # Anthropic
                ]
                
                agent = MultiModelAgent(
                    primary_model=openai_model,
                    fallback_models=[anthropic_model],
                    evaluator=evaluator
                )
                
                response = await agent.process_message("Test message with evaluation")
                assert "Anthropic response" in response
                assert agent.current_model == anthropic_model

@pytest.mark.asyncio
async def test_concurrent_model_requests():
    """Test handling multiple concurrent requests across models."""
    openai_model = OpenAIIntegration()
    anthropic_model = AnthropicIntegration()
    evaluator = ResponseEvaluator()
    
    with patch.object(openai_model, 'generate_response') as mock_openai:
        with patch.object(anthropic_model, 'generate_response') as mock_anthropic:
            mock_openai.side_effect = [f"OpenAI response {i}" for i in range(3)]
            mock_anthropic.side_effect = [f"Anthropic response {i}" for i in range(3)]
            
            agent = MultiModelAgent(
                primary_model=openai_model,
                fallback_models=[anthropic_model],
                evaluator=evaluator
            )
            
            messages = ["Message 1", "Message 2", "Message 3"]
            tasks = [agent.process_message(msg) for msg in messages]
            responses = await asyncio.gather(*tasks)
            
            assert len(responses) == len(messages)
            assert all(isinstance(response, str) for response in responses)

@pytest.mark.asyncio
async def test_model_context_preservation():
    """Test that model context is preserved across multiple interactions."""
    openai_model = OpenAIIntegration()
    evaluator = ResponseEvaluator()
    
    conversation = [
        "What is the capital of France?",
        "Tell me more about its history",
        "What famous landmarks are there?"
    ]
    
    with patch.object(openai_model, 'generate_response') as mock_generate:
        mock_generate.side_effect = [
            "Paris is the capital of France.",
            "Paris has a rich history dating back to...",
            "The Eiffel Tower is the most famous landmark..."
        ]
        
        agent = MultiModelAgent(
            primary_model=openai_model,
            fallback_models=[],
            evaluator=evaluator
        )
        
        responses = []
        for message in conversation:
            response = await agent.process_message(message)
            responses.append(response)
        
        assert len(responses) == len(conversation)
        assert all("Paris" in response for response in responses)
        assert agent.get_history()[-1]["message"] == conversation[-1]

@pytest.mark.asyncio
async def test_model_error_recovery():
    """Test system recovery after model errors."""
    openai_model = OpenAIIntegration()
    anthropic_model = AnthropicIntegration()
    evaluator = ResponseEvaluator()
    
    with patch.object(openai_model, 'generate_response') as mock_openai:
        with patch.object(anthropic_model, 'generate_response') as mock_anthropic:
            # Configure OpenAI to fail then recover
            mock_openai.side_effect = [
                ModelError("API Error"),  # First call fails
                "OpenAI recovered response"  # Second call succeeds
            ]
            
            # Configure Anthropic as fallback
            mock_anthropic.return_value = "Anthropic fallback response"
            
            agent = MultiModelAgent(
                primary_model=openai_model,
                fallback_models=[anthropic_model],
                evaluator=evaluator
            )
            
            # First request - OpenAI fails, falls back to Anthropic
            response1 = await agent.process_message("Test message 1")
            assert "Anthropic fallback response" in response1
            assert agent.current_model == anthropic_model
            
            # Second request - Try OpenAI again, succeeds
            response2 = await agent.process_message("Test message 2")
            assert "OpenAI recovered response" in response2
            assert agent.current_model == openai_model 