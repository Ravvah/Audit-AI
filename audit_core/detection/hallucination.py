"""
Hallucination detection for LLM responses
"""
import re
import numpy as np
from typing import Dict, Any, List, Tuple, Optional
import logging

from sentence_transformers import SentenceTransformer, util

logger = logging.getLogger("audit_core.detection")

class HallucinationDetector:
    """
    Detects hallucinations in LLM responses.
    """
    
    def __init__(self, embeddings_provider=None):
        """
        Initialize the hallucination detector.
        
        Args:
            embeddings_provider: Optional provider for advanced detection methods
        """
        # Use a lightweight MiniLM model for embeddings
        self.embedder = embeddings_provider or SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    
    def score_hallucination(self, prompt: str, completion: str) -> float:
        """
        Calculate a hallucination score for a prompt/response pair.
        
        A higher score indicates higher probability of hallucination.
        
        Args:
            prompt: Input text
            completion: Generated response
            
        Returns:
            float: Hallucination score between 0.0 (no hallucination) and 1.0 (complete hallucination)
        """
        try:
            # Simple heuristic-based score
            return self._heuristic_score(prompt, completion)
        except Exception as e:
            logger.error(f"Error calculating hallucination score: {e}")
            return 0.5  # Default value in case of error
    
    def _heuristic_score(self, prompt: str, completion: str) -> float:
        """
        Calculate hallucination score based on simple heuristics.
        
        Args:
            prompt: Input text
            completion: Generated response
            
        Returns:
            float: Hallucination score
        """
        # Normalize texts
        prompt_lower = prompt.lower()
        completion_lower = completion.lower()
        
        # Keywords potentially indicating hallucinations
        hallucination_indicators = [
            "i'm not sure",
            "i don't know",
            "i think",
            "perhaps",
            "probably",
            "it's possible",
            "might be",
            "it's likely",
            "it's probable",

        ]
        
        # Calculate hesitation score
        hesitation_score = 0.0
        for indicator in hallucination_indicators:
            if indicator in completion_lower:
                hesitation_score += 0.1
        hesitation_score = min(hesitation_score, 0.5)
        
        # Calculate word overlap between prompt and response
        prompt_words = set(re.findall(r'\b\w+\b', prompt_lower))
        completion_words = set(re.findall(r'\b\w+\b', completion_lower))
        
        if len(prompt_words) == 0 or len(completion_words) == 0:
            overlap_score = 0.5
        else:
            # More words in common suggests lower hallucination
            common_words = prompt_words.intersection(completion_words)
            overlap_ratio = len(common_words) / max(1, len(completion_words))
            overlap_score = max(0, 0.7 - overlap_ratio)
        
        # Semantic divergence score: 1 - cosine similarity between prompt and completion
        try:
            prompt_emb = self.embedder.encode(prompt, convert_to_tensor=True)
            completion_emb = self.embedder.encode(completion, convert_to_tensor=True)
            sim = util.pytorch_cos_sim(prompt_emb, completion_emb).item()
            semantic_divergence = 1 - sim
        except Exception as e:
            logger.warning(f"Semantic similarity computation failed: {e}")
            semantic_divergence = 0.5

        # Weighted combination: emphasize semantic divergence over heuristics
        # Assign weights: semantic_divergence=0.6, hesitation_score=0.2, overlap_score=0.2
        weighted_sum = (semantic_divergence * 0.6) + (hesitation_score * 0.2) + (overlap_score * 0.2)
        hallucination_score = weighted_sum

        # Clamp to [0,1]
        return float(np.clip(hallucination_score, 0.0, 1.0))
    
    def get_fact_consistency(self, prompt: str, completion: str) -> float:
        """
        Evaluate factual consistency between prompt and response.
        
        Args:
            prompt: Input text
            completion: Generated response
            
        Returns:
            float: Factual consistency score between 0.0 (inconsistent) and 1.0 (consistent)
        """
        # Simplified: use inverse of hallucination score as proxy
        hallucination_score = self.score_hallucination(prompt, completion)
        return 1.0 - hallucination_score