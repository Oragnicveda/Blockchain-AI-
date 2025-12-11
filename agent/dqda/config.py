import os
from dataclasses import dataclass, field
from typing import Dict

@dataclass
class DQDAConfig:
    """Configuration for DQDA Agent."""
    
    # Output
    OUTPUT_DIR: str = os.getenv("DQDA_OUTPUT_DIR", "output/dqda")
    
    # Scoring Weights
    SCORING_WEIGHTS: Dict[str, float] = field(default_factory=lambda: {
        "team": 0.3,
        "market": 0.2,
        "product": 0.2,
        "tokenomics": 0.15,
        "traction": 0.15
    })
    
    # Rate Limiting
    RATE_LIMIT_DELAY: float = float(os.getenv("DQDA_RATE_LIMIT_DELAY", "1.0"))
    
    def get_weight(self, category: str) -> float:
        return self.SCORING_WEIGHTS.get(category, 0.0)

    def ensure_output_dir(self):
        """Ensure the output directory exists."""
        if not os.path.exists(self.OUTPUT_DIR):
            os.makedirs(self.OUTPUT_DIR)
