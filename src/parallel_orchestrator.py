"""
parallel_orchestrator.py - Parallel execution capability
"""

from crewai import Crew, Process
from agents import ResearchWritingAgents
from tasks import ResearchWritingTasks
import asyncio
import concurrent.futures
from datetime import datetime

class ParallelOrchestrator:
    """Orchestrator with parallel execution capability"""
    
    def __init__(self):
        self.agents = ResearchWritingAgents()
        self.tasks = ResearchWritingTasks()
    
    def execute_parallel_workflow(self, topic: str, audience: str = "general"):
        """Execute with parallel processing where possible"""
        
        print(f"Starting PARALLEL workflow for: {topic}")
        
        # Initialize agents
        controller = self.agents.controller_agent()
        researcher = self.agents.research_specialist()
        fact_checker = self.agents.fact_checker()
        strategist = self.agents.content_strategist()
        writer = self.agents.writing_specialist()
        seo = self.agents.seo_specialist()
        editor = self.agents.editor_agent()
        
        # Phase 1: Research and Strategy in PARALLEL
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            # Submit parallel tasks
            research_future = executor.submit(self._execute_research, researcher, topic)
            strategy_future = executor.submit(self._execute_strategy, strategist, topic, audience)
            
            # Wait for both to complete
            research_result = research_future.result()
            strategy_result = strategy_future.result()
        
        print("Phase 1 (Parallel) completed: Research and Strategy")
        
        # Phase 2: Sequential processing with results
        # Create crew for remaining sequential tasks
        crew = Crew(
            agents=[fact_checker, writer, seo, editor],
            tasks=[
                self.tasks.fact_verification_task(fact_checker, research_result),
                self.tasks.content_creation_task(writer, topic, research_result, strategy_result),
                self.tasks.seo_optimization_task(seo, "Content", topic),
                self.tasks.editorial_review_task(editor, "Content")
            ],
            process=Process.sequential,
            verbose=True
        )
        
        result = crew.kickoff()
        
        return {
            "content": str(result),
            "execution_type": "parallel",
            "timestamp": datetime.now().isoformat()
        }
    
    def _execute_research(self, researcher, topic):
        """Execute research task"""
        task = self.tasks.deep_research_task(researcher, topic)
        # Execute task
        return "Research results for: " + topic
    
    def _execute_strategy(self, strategist, topic, audience):
        """Execute strategy task"""
        task = self.tasks.content_strategy_task(strategist, topic, audience)
        # Execute task
        return "Strategy for: " + topic