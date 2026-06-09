"""
orchestrator.py - Main orchestration system for the Research and Writing Assistant
Fixed for Windows path issues and corrected method names
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import logging
import json
from crewai import Crew, Process
from agents import ResearchWritingAgents
from tasks import ResearchWritingTasks
from tools import SourceCredibilityAnalyzer, ContentOptimizer

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(process)d - %(name)s - %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('workflow.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class ResearchWritingOrchestrator:
    """Main orchestrator that manages the entire workflow"""
    
    def __init__(self):
        """Initialize the orchestrator with agents and tasks"""
        logger.info("Initializing ResearchWritingOrchestrator...")
        
        # Fix Windows path issues
        self._setup_windows_environment()
        
        self.agents = ResearchWritingAgents()
        self.tasks = ResearchWritingTasks()
        self.credibility_analyzer = SourceCredibilityAnalyzer()
        self.content_optimizer = ContentOptimizer()
        
        # Create output directories
        os.makedirs('outputs', exist_ok=True)
        os.makedirs('logs', exist_ok=True)
        
        logger.info("Orchestrator initialized successfully")
    
    def _setup_windows_environment(self):
        """Setup environment for Windows compatibility"""
        try:
            # Set a custom cache directory to avoid long paths
            cache_dir = Path.cwd() / "crew_cache"
            cache_dir.mkdir(exist_ok=True)
            
            # Set environment variable for CrewAI cache
            os.environ['CREWAI_STORAGE_DIR'] = str(cache_dir)
            
            # Create subdirectories
            for subdir in ['short_term', 'long_term', 'entities']:
                (cache_dir / subdir).mkdir(exist_ok=True)
            
            logger.info(f"Cache directory set to: {cache_dir}")
            
        except Exception as e:
            logger.warning(f"Could not setup cache directory: {e}")
    
    def execute_workflow(self, topic: str, audience: str = "general", mode: str = "sequential"):
        """Execute the complete research and writing workflow"""
        
        logger.info(f"Starting workflow for topic: {topic}")
        start_time = datetime.now()
        
        try:
            # Initialize agents
            controller = self.agents.controller_agent()
            researcher = self.agents.research_specialist()
            fact_checker = self.agents.fact_checker()
            strategist = self.agents.content_strategist()
            writer = self.agents.writing_specialist()
            seo = self.agents.seo_specialist()
            editor = self.agents.editor_agent()
            
            # Add custom tool to researcher
            researcher.tools.append(self.credibility_analyzer)
            
            # Create tasks with proper context passing
            research_plan_task = self.tasks.research_planning_task(
                agent=controller, 
                topic=topic
            )
            
            deep_research_task = self.tasks.deep_research_task(
                agent=researcher, 
                topic=topic
            )
            
            fact_check_task = self.tasks.fact_verification_task(
                agent=fact_checker,
                research="[Will be provided from previous task]"
            )
            
            content_strategy_task = self.tasks.content_strategy_task(
                agent=strategist,
                topic=topic,
                audience=audience
            )
            
            # Use content_creation_task (correct method name from tasks.py)
            writing_task = self.tasks.content_creation_task(
                agent=writer,
                topic=topic,
                research="[Will be provided from previous tasks]",
                strategy="[Will be provided from strategy task]"
            )
            
            seo_task = self.tasks.seo_optimization_task(
                agent=seo,
                content="[Will be provided from writing task]",
                topic=topic
            )
            
            # Use editorial_review_task (correct method name from tasks.py)
            editing_task = self.tasks.editorial_review_task(
                agent=editor,
                content="[Will be provided from SEO task]"
            )
            
            # Set task contexts for sequential flow
            deep_research_task.context = [research_plan_task]
            fact_check_task.context = [deep_research_task]
            content_strategy_task.context = [fact_check_task]
            writing_task.context = [content_strategy_task, fact_check_task]
            seo_task.context = [writing_task]
            editing_task.context = [seo_task]
            
            # Create crew with Windows-compatible settings
            crew = Crew(
                agents=[controller, researcher, fact_checker, strategist, 
                       writer, seo, editor],
                tasks=[research_plan_task, deep_research_task, fact_check_task,
                      content_strategy_task, writing_task, seo_task, editing_task],
                process=Process.sequential if mode == "sequential" else Process.hierarchical,
                manager_llm=controller.llm if mode == "hierarchical" else None,
                verbose=True,
                # Disable memory to avoid Windows path issues
                memory=False,
                embedder={
                    "provider": "openai",
                    "config": {
                        "api_key": os.getenv("OPENAI_API_KEY"),
                        "model": "text-embedding-3-small"
                    }
                },
                # Additional settings to prevent path issues
                max_rpm=10,
                share_crew=False
            )
            
            # Execute the workflow
            logger.info("Starting crew execution...")
            result = crew.kickoff()
            
            # Process and save results
            self._save_results(topic, result, start_time)
            
            logger.info("Workflow completed successfully!")
            return result
            
        except Exception as e:
            logger.error(f"Workflow failed: {str(e)}", exc_info=True)
            raise
    
    def _save_results(self, topic: str, result, start_time):
        """Save the results to files"""
        try:
            # Create timestamp for filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Sanitize topic for filename
            safe_topic = "".join(c if c.isalnum() or c in " -_" else "_" for c in topic)
            safe_topic = safe_topic.replace(" ", "_")[:50]
            
            # Save main output
            output_file = f"outputs/{safe_topic}_{timestamp}.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"# Research and Writing Output\n\n")
                f.write(f"**Topic:** {topic}\n")
                f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"**Duration:** {datetime.now() - start_time}\n\n")
                f.write("---\n\n")
                
                # Handle different result types
                if hasattr(result, 'raw'):
                    f.write(str(result.raw))
                else:
                    f.write(str(result))
            
            logger.info(f"Output saved to {output_file}")
            
            # Save metadata
            metadata = {
                "topic": topic,
                "timestamp": timestamp,
                "duration": str(datetime.now() - start_time),
                "output_file": output_file
            }
            
            metadata_file = f"outputs/{safe_topic}_{timestamp}_metadata.json"
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            logger.info(f"Metadata saved to {metadata_file}")
            
        except Exception as e:
            logger.error(f"Failed to save results: {str(e)}")

# Create convenience function for main.py
def run_orchestrator(topic: str, audience: str = "general", mode: str = "sequential"):
    """Convenience function to run the orchestrator"""
    orchestrator = ResearchWritingOrchestrator()
    
    return orchestrator.execute_workflow(topic, audience, mode)