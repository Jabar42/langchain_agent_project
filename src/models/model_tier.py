from enum import Enum

class ModelTier(Enum):
    """Defines the tier/capability level of a model.
    
    Tiers are ordered from basic to premium, representing increasing levels of capability:
    - BASIC: Simple models with limited capabilities
    - STANDARD: General-purpose models with good performance
    - ADVANCED: More capable models with better quality
    - PREMIUM: Top-tier models with the best performance
    """
    BASIC = 1
    STANDARD = 2
    ADVANCED = 3
    PREMIUM = 4
    
    def __lt__(self, other):
        if not isinstance(other, ModelTier):
            return NotImplemented
        return self.value < other.value
    
    def __le__(self, other):
        if not isinstance(other, ModelTier):
            return NotImplemented
        return self.value <= other.value
    
    def __gt__(self, other):
        if not isinstance(other, ModelTier):
            return NotImplemented
        return self.value > other.value
    
    def __ge__(self, other):
        if not isinstance(other, ModelTier):
            return NotImplemented
        return self.value >= other.value 