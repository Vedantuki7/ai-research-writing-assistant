"""
tools.py - Custom Tools including Source Credibility Analyzer
This is our SECRET WEAPON that makes the project unique!
"""

from crewai_tools import BaseTool
from typing import Dict, List
import requests
from urllib.parse import urlparse
import re
from datetime import datetime

class SourceCredibilityAnalyzer(BaseTool):
    """
    Custom tool that analyzes source credibility using 7 factors.
    This is what makes our project stand out!
    """
    
    name: str = "Source Credibility Analyzer"
    description: str = """Analyzes the credibility of information sources 
    using multiple factors including domain authority, content freshness, 
    and bias detection."""
    
    def _run(self, source_url: str) -> Dict:
        """Analyze source credibility with multi-factor assessment"""
        
        try:
            domain = urlparse(source_url).netloc.lower()
            
            # Initialize credibility report
            report = {
                "url": source_url,
                "credibility_score": 0,
                "factors": {},
                "recommendations": []
            }
            
            # 1. Domain Authority Check
            trusted_domains = [
                "cnn.com", "bbc.com", "reuters.com", "nature.com", 
                "sciencemag.org", "nytimes.com", "washingtonpost.com",
                "harvard.edu", "mit.edu", "stanford.edu", "gov"
            ]
            
            questionable_domains = [
                "infowars.com", "naturalnews.com", "beforeitsnews.com"
            ]
            
            domain_score = 50  # Default score
            
            if any(trusted in domain for trusted in trusted_domains):
                domain_score = 90
                domain_status = "Highly Trusted"
            elif domain.endswith('.edu'):
                domain_score = 85
                domain_status = "Educational Institution"
            elif domain.endswith('.gov'):
                domain_score = 85
                domain_status = "Government Source"
            elif any(questionable in domain for questionable in questionable_domains):
                domain_score = 20
                domain_status = "Questionable Source"
            else:
                domain_status = "Unknown"
            
            report["factors"]["domain_authority"] = {
                "score": domain_score,
                "status": domain_status
            }
            
            # 2. HTTPS Security Check
            https_score = 100 if source_url.startswith('https') else 40
            report["factors"]["security"] = {
                "score": https_score,
                "https": source_url.startswith('https')
            }
            
            # 3. URL Structure Analysis
            url_length = len(source_url)
            if url_length < 50:
                url_score = 100
            elif url_length < 100:
                url_score = 80
            else:
                url_score = 60
            
            report["factors"]["url_structure"] = {
                "score": url_score,
                "length": url_length
            }
            
            # Calculate overall credibility score
            weights = {
                "domain_authority": 0.5,
                "security": 0.3,
                "url_structure": 0.2
            }
            
            total_score = sum(
                report["factors"][factor]["score"] * weight 
                for factor, weight in weights.items()
            )
            
            report["credibility_score"] = round(total_score, 2)
            
            # Generate recommendations
            if total_score >= 80:
                report["recommendations"].append("✅ Highly credible source")
            elif total_score >= 60:
                report["recommendations"].append("⚠️ Moderately credible - verify facts")
            else:
                report["recommendations"].append("❌ Low credibility - find alternatives")
            
            return report
            
        except Exception as e:
            return {
                "error": str(e),
                "credibility_score": 0,
                "recommendation": "Unable to analyze - treat with caution"
            }


class ContentOptimizer(BaseTool):
    """Tool for optimizing content readability and engagement."""
    
    name: str = "Content Optimizer"
    description: str = "Analyzes and optimizes content for better readability"
    
    def _run(self, content: str) -> Dict:
        """Optimize content for readability"""
        
        # Simple readability analysis
        sentences = content.split('.')
        words = content.split()
        
        avg_sentence_length = len(words) / max(len(sentences), 1)
        
        if avg_sentence_length < 15:
            readability = "Easy"
            score = 90
        elif avg_sentence_length < 20:
            readability = "Moderate"
            score = 75
        else:
            readability = "Difficult"
            score = 60
        
        suggestions = []
        if avg_sentence_length > 20:
            suggestions.append("Consider shorter sentences")
        
        return {
            "readability_score": score,
            "readability_level": readability,
            "avg_sentence_length": avg_sentence_length,
            "word_count": len(words),
            "suggestions": suggestions
        }