"""
tasks.py - Task definitions for the Research and Writing System
Enhanced with RAG integration and output limits
"""

from crewai import Task
from typing import List, Optional

class ResearchWritingTasks:
    """Factory class for creating tasks"""
    
    def research_planning_task(self, agent, topic: str):
        """Task for planning the research approach"""
        return Task(
            description=f"""
            Create a comprehensive research plan for: {topic}
            
            Include:
            1. Key research questions
            2. Types of sources to consult
            3. Research methodology
            4. Potential challenges
            
            Output a structured research plan.
            """,
            agent=agent,
            expected_output="Detailed research plan with methodology"
        )
    
    def deep_research_task(self, agent, topic: str):
        """Task for conducting comprehensive research"""
        return Task(
            description=f"""
            Research '{topic}' thoroughly using multiple sources.
            
            Requirements:
            - Use at least 5 credible sources
            - Include recent information
            - Cover multiple perspectives
            - Check source credibility
            - Provide citations
            
            Compile findings into a research report.
            """,
            agent=agent,
            expected_output="Comprehensive research report with citations"
        )
    
    def fact_verification_task(self, agent, research: str):
        """Task for verifying facts and claims"""
        return Task(
            description=f"""
            Verify all facts in this research:
            {research[:500]}...
            
            Check:
            - Accuracy of statistics
            - Currency of information
            - Source reliability
            - Conflicting information
            
            Rate confidence level for each claim.
            """,
            agent=agent,
            expected_output="Fact-check report with confidence ratings"
        )
    
    def content_strategy_task(self, agent, topic: str, audience: str):
        """Task for developing content strategy"""
        return Task(
            description=f"""
            Create content strategy for '{topic}'
            Target audience: {audience}
            
            Include:
            - Content objectives
            - Key messages
            - Structure outline
            - Engagement tactics
            - Call-to-action
            
            Output a strategic blueprint.
            """,
            agent=agent,
            expected_output="Content strategy with structure outline"
        )
    
    def content_creation_task(self, agent, topic: str, research: str, strategy: str):
        """Task for creating the actual content"""
        return Task(
            description=f"""
            Write engaging content about '{topic}'
            
            Using research: {research[:300]}...
            Following strategy: {strategy[:300]}...
            
            Requirements:
            - 1000-1500 words
            - Engaging introduction
            - Clear structure
            - Evidence-based arguments
            - Strong conclusion
            
            Create publication-ready content.
            """,
            agent=agent,
            expected_output="High-quality written content"
        )
    
    def seo_optimization_task(self, agent, content: str, topic: str):
        """Task for SEO optimization"""
        return Task(
            description=f"""
            Optimize this content for search engines:
            {content[:500]}...
            
            Topic focus: {topic}
            
            Tasks:
            - Research keywords
            - Optimize headings
            - Create meta description
            - Ensure keyword density
            - Suggest links
            
            Provide SEO-optimized version.
            """,
            agent=agent,
            expected_output="SEO-optimized content with recommendations"
        )
    
    def editorial_review_task(self, agent, content: str):
        """Task for final editing"""
        return Task(
            description=f"""
            Perform final edit of:
            {content[:500]}...
            
            Check:
            - Grammar and spelling
            - Style consistency
            - Clarity and flow
            - Professional tone
            
            Deliver polished final version.
            """,
            agent=agent,
            expected_output="Professionally edited final content"
        )
    
    # ============================================================
    # NEW METHODS FOR RAG INTEGRATION AND OUTPUT LIMITS
    # ============================================================
    
    def create_custom_task(self, description: str, agent, expected_output: str):
        """Create a task with custom parameters"""
        return Task(
            description=description,
            agent=agent,
            expected_output=expected_output
        )
    
    def research_task_with_rag_context(self, agent, topic: str, rag_context: str = "", max_words: int = 750):
        """Enhanced research task with RAG context and strict limits"""
        return Task(
            description=f"""
            Research '{topic}' efficiently.
            
            EXISTING KNOWLEDGE FROM DATABASE:
            {rag_context[:500] if rag_context else 'No prior knowledge available'}
            
            STRICT REQUIREMENTS:
            - Maximum 3 research iterations
            - Use only top 5 most credible sources
            - Focus on NEW information not in existing knowledge
            - Provide concise summary ({max_words} words MAXIMUM)
            - Include source citations
            - STOP after finding sufficient information
            
            DO NOT continue researching indefinitely.
            """,
            agent=agent,
            expected_output=f"Concise research report ({max_words} words max) with citations"
        )
    
    def content_creation_with_limit(self, agent, topic: str, research: str = "", max_words: int = 1200):
        """Content creation with strict word limit"""
        return Task(
            description=f"""
            Write an article about '{topic}'
            
            Research provided: {research[:500] if research else 'Use your knowledge'}...
            
            STRICT REQUIREMENTS:
            - Length: {max_words} words MAXIMUM
            - Structure: 
              * Introduction (150 words)
              * 3 main sections (300 words each)
              * Conclusion (150 words)
            - Style: Clear, engaging, informative
            - MUST STOP when reaching word limit
            
            Create a complete, well-structured article.
            NO ADDITIONAL COMMENTARY - just the article.
            """,
            agent=agent,
            expected_output=f"Complete article ({max_words} words maximum)"
        )
    
    def quick_edit_task(self, agent, content: str, max_words: int = 1200):
        """Quick editing task with word limit enforcement"""
        return Task(
            description=f"""
            Quickly polish this article:
            {content[:500]}...
            
            REQUIREMENTS:
            - Fix grammar and spelling errors
            - Ensure smooth flow
            - Verify word count is under {max_words} words
            - If over limit, trim to fit
            - Make it publication-ready
            
            RETURN ONLY the final article, no commentary.
            """,
            agent=agent,
            expected_output="Final polished article"
        )
    
    def research_with_limit(self, agent, topic: str, max_iterations: int = 3):
        """Research task with iteration limit"""
        return Task(
            description=f"""
            Research '{topic}' with efficiency focus.
            
            HARD LIMITS:
            - Maximum {max_iterations} search iterations
            - Maximum 5 sources total
            - Maximum 750 words output
            - Focus on quality over quantity
            
            STOP after {max_iterations} iterations regardless of findings.
            Provide what you have found within these limits.
            """,
            agent=agent,
            expected_output="Limited research summary (750 words max)"
        )
    
    def integrated_writing_task(self, agent, topic: str, rag_info: str = "", research_info: str = ""):
        """Writing task that integrates RAG and research findings"""
        return Task(
            description=f"""
            Write a comprehensive article about '{topic}'
            
            KNOWLEDGE BASE INFORMATION:
            {rag_info[:400] if rag_info else 'None available'}
            
            NEW RESEARCH FINDINGS:
            {research_info[:400] if research_info else 'None available'}
            
            REQUIREMENTS:
            - Integrate both knowledge base and new research
            - Maximum 1200 words
            - Professional tone
            - Clear structure with sections
            - Include introduction and conclusion
            
            OUTPUT ONLY the article text, nothing else.
            """,
            agent=agent,
            expected_output="Integrated article (1200 words max)"
        )