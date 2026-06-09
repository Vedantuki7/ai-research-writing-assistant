"""
agents.py - Multi-Agent Research and Writing System
This module defines all AI agents with specific roles and capabilities.
"""

from crewai import Agent
from langchain_openai import ChatOpenAI
from crewai_tools import SerperDevTool, WebsiteSearchTool, FileReadTool
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ResearchWritingAgents:
    """Factory class for creating specialized AI agents."""
    
    def _get_llm(self):
        return ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.7,
            api_key=os.getenv("OPENAI_API_KEY")
        )
    
    def __init__(self):
        """Initialize tools for agents to use"""
        self.search_tool = SerperDevTool(api_key=os.getenv("SERPER_API_KEY"))
        self.website_tool = WebsiteSearchTool()
        self.file_tool = FileReadTool()
    
    def controller_agent(self):
        """Create the main controller agent that orchestrates the workflow."""
        return Agent(
            role="Project Controller",
            goal="Orchestrate research and writing tasks efficiently",
            backstory="""You are an experienced project manager with 15 years 
            managing research teams. You excel at breaking down complex projects 
            and ensuring quality output.""",
            verbose=True,
            allow_delegation=True,
            llm=self._get_llm()
        )
    
    def research_specialist(self):
        """Agent specialized in deep research and information gathering."""
        return Agent(
            role="Senior Research Specialist",
            goal="Conduct comprehensive research from multiple credible sources",
            backstory="""You are a PhD researcher with 20 years of experience. 
            You're meticulous about source credibility and always verify 
            information from multiple sources.""",
            verbose=True,
            tools=[self.search_tool, self.website_tool],
            llm=self._get_llm()
        )
    
    def fact_checker(self):
        """Agent dedicated to verifying information accuracy."""
        return Agent(
            role="Fact Verification Specialist",
            goal="Verify all facts and claims for accuracy",
            backstory="""You worked as a fact-checker for major publications 
            for 12 years. You have a detective's mindset and never let false 
            information slip through.""",
            verbose=True,
            tools=[self.search_tool],
            llm=self._get_llm()
        )
    
    def content_strategist(self):
        """Agent that plans content structure and strategy."""
        return Agent(
            role="Content Strategy Director",
            goal="Design optimal content structure and strategy",
            backstory="""You've been a content strategist for Fortune 500 
            companies for 15 years. You understand how to structure information 
            for maximum impact and engagement.""",
            verbose=True,
            llm=self._get_llm()
        )
    
    def writing_specialist(self):
        """Agent specialized in creating high-quality written content."""
        return Agent(
            role="Senior Content Writer",
            goal="Transform research into compelling written content",
            backstory="""You're an award-winning writer with 18 years of 
            experience. You have a gift for making complex topics accessible 
            and engaging.""",
            verbose=True,
            llm=self._get_llm()
        )
    
    def seo_specialist(self):
        """Agent focused on search engine optimization."""
        return Agent(
            role="SEO Optimization Expert",
            goal="Optimize content for search engines",
            backstory="""You've been doing SEO for 10 years and have helped 
            hundreds of websites reach the first page of Google.""",
            verbose=True,
            tools=[self.search_tool],
            llm=self._get_llm()
        )
    
    def editor_agent(self):
        """Agent responsible for final editing and quality assurance."""
        return Agent(
            role="Chief Editor",
            goal="Ensure highest quality standards for all content",
            backstory="""You're a veteran editor with 25 years at top 
            publications. You have an eagle eye for errors and know what 
            makes content exceptional.""",
            verbose=True,
            llm=self._get_llm()
        )