# safety.py
import re
from typing import Dict, List, Tuple

class SafetyValidator:
    """Validates inputs and outputs for safety"""
    
    def __init__(self):
        # Blocked patterns (basic safety)
        self.blocked_patterns = [
            r"ignore previous instructions",
            r"disregard",
            r"you are now",
            r"new instructions",
            r"system prompt",
            r"reveal your prompt"
        ]
        
        # Sensitive data patterns
        self.sensitive_patterns = {
            "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
            "credit_card": r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",
            "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            "phone": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b"
        }
    
    def validate_input(self, query: str) -> Tuple[bool, str, List[str]]:
        """
        Validate user input for safety issues
        
        Returns:
            (is_valid, sanitized_query, warnings)
        """
        warnings = []
        
        # Check if input is empty
        if not query or len(query.strip()) == 0:
            return False, "", ["Input cannot be empty"]
        
        # Check for prompt injection attempts
        query_lower = query.lower()
        for pattern in self.blocked_patterns:
            if re.search(pattern, query_lower):
                warnings.append(f"Potential prompt injection detected: '{pattern}'")
                return False, "", warnings
        
        # Check for sensitive data
        for data_type, pattern in self.sensitive_patterns.items():
            if re.search(pattern, query):
                warnings.append(f"Potential {data_type} detected in input")
                # Redact it
                query = re.sub(pattern, f"[REDACTED_{data_type.upper()}]", query)
        
        # Length check
        if len(query) > 5000:
            warnings.append("Input too long (max 5000 characters)")
            return False, "", warnings
        
        return True, query, warnings
    
    def validate_output(self, output: str) -> Tuple[bool, str, List[str]]:
        """
        Validate agent output for safety
        
        Returns:
            (is_valid, sanitized_output, warnings)
        """
        warnings = []
        
        # Check for sensitive data in output
        for data_type, pattern in self.sensitive_patterns.items():
            if re.search(pattern, output):
                warnings.append(f"Sensitive {data_type} found in output - redacted")
                output = re.sub(pattern, f"[REDACTED_{data_type.upper()}]", output)
        
        # Check for harmful content markers
        harmful_indicators = [
            "how to hack",
            "illegal",
            "bypass security",
            "exploit vulnerability"
        ]
        
        output_lower = output.lower()
        for indicator in harmful_indicators:
            if indicator in output_lower:
                warnings.append(f"Potentially harmful content detected: {indicator}")
                return False, "", warnings
        
        return True, output, warnings


class ConfidenceScorer:
    """Calculate confidence scores for agent outputs"""
    
    @staticmethod
    def calculate_confidence(output: str, agent_name: str) -> float:
        """
        Calculate confidence score (0-1) based on output quality
        
        Simple heuristics:
        - Length check (too short = low confidence)
        - Uncertainty phrases
        - Specificity
        """
        confidence = 1.0
        
        # Length check
        if len(output) < 50:
            confidence -= 0.3
        
        # Check for uncertainty phrases
        uncertainty_phrases = [
            "i'm not sure",
            "maybe",
            "possibly",
            "i don't know",
            "unclear",
            "uncertain"
        ]
        
        output_lower = output.lower()
        for phrase in uncertainty_phrases:
            if phrase in output_lower:
                confidence -= 0.2
                break
        
        # Check for specificity (numbers, dates, concrete details)
        has_numbers = bool(re.search(r'\d+', output))
        has_specifics = bool(re.search(r'(percent|%|dollars|\$|Q[1-4]|january|february|march)', output_lower))
        
        if has_numbers:
            confidence += 0.1
        if has_specifics:
            confidence += 0.1
        
        # Clamp between 0 and 1
        return max(0.0, min(1.0, confidence))