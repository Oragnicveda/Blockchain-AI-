from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
from agent.dqda.data_collectors.base_collector import DQDADataPoint

@dataclass
class DealInput:
    """Input data for a deal qualification request."""
    startup_name: str = "Unknown Startup"
    pitch_deck_path: Optional[str] = None
    website_url: Optional[str] = None
    whitepaper_path: Optional[str] = None
    token_symbol: Optional[str] = None
    additional_keywords: List[str] = field(default_factory=list)

@dataclass
class DealAssessment:
    """Assessment result for a deal."""
    startup_name: str
    overall_score: float
    confidence_score: float
    data_points: List[DQDADataPoint] = field(default_factory=list)
    category_scores: Dict[str, float] = field(default_factory=dict)
    flags: List[str] = field(default_factory=list) # e.g. "Missing Team", "High Risk"
    assessment_timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "startup_name": self.startup_name,
            "overall_score": self.overall_score,
            "confidence_score": self.confidence_score,
            "data_points": [dp.to_dict() for dp in self.data_points],
            "category_scores": self.category_scores,
            "flags": self.flags,
            "assessment_timestamp": self.assessment_timestamp.isoformat()
        }
