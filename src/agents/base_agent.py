from abc import ABC, abstractmethod
from typing import List, Dict, Any
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.schema import BaseLanguageModel
from datetime import datetime

class BaseAgent(ABC):
    """Base agent class that defines the interface for all agents in the system."""
    
    def __init__(self, llm: BaseLanguageModel):
        self.llm = llm
        self.history: List[Dict[str, Any]] = []
        
    @abstractmethod
    async def process_message(self, message: str) -> str:
        """Process an incoming message and return a response."""
        pass
    
    @abstractmethod
    async def handle_error(self, error: Exception) -> str:
        """Handle any errors that occur during message processing."""
        pass
    
    def add_to_history(self, message: str, response: str):
        """Add an interaction to the conversation history."""
        self.history.append({
            "message": message,
            "response": response,
            "timestamp": datetime.now().isoformat()
        })
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Retrieve the conversation history."""
        return self.history
    
    @abstractmethod
    async def validate_response(self, response: str) -> bool:
        """Validate if a response meets quality criteria."""
        pass 