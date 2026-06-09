"""
Enhanced Orchestrator with RAG Integration and Output Limits
Fixed with correct agent method names
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime
from crewai import Crew, Process, Task

# Fix imports - use src prefix since we're calling from root
from src.agents import ResearchWritingAgents
from src.tasks import ResearchWritingTasks
from src.rag_system import RAGKnowledgeBase

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedOrchestrator:
    ACTIVE_AGENTS = ["researcher", "writer", "editor"]
    
    def __init__(self):
        """Initialize with RAG and agents"""
        logger.info("Initializing Enhanced Orchestrator...")
        
        self.agents = ResearchWritingAgents()
        self.tasks = ResearchWritingTasks()
        
        # Initialize RAG
        logger.info("Loading RAG system...")
        self.rag = RAGKnowledgeBase()
        if not self.rag.load_knowledge_base():
            logger.info("Building knowledge base...")
            self.rag.build_knowledge_base()
        
        # Set strict limits to prevent infinite loops
        self.max_iterations = 3
        self.max_research_words = 750
        self.max_article_words = 1200
        
        logger.info("✅ Enhanced Orchestrator ready")
    
    def run_integrated_workflow(self, topic: str, audience: str = "general"):
        """Run the complete integrated workflow with RAG + Agents"""
        
        print("\n" + "="*60)
        print(f"🚀 INTEGRATED WORKFLOW: {topic}")
        print("="*60)
        
        # PHASE 1: Check RAG Knowledge Base
        print("\n📚 PHASE 1: Checking Knowledge Base...")
        rag_results = self.rag.retrieve(topic, k=3)
        
        rag_context = ""
        if rag_results:
            print(f"✅ Found {len(rag_results)} relevant documents:")
            for i, result in enumerate(rag_results[:3], 1):
                print(f"   {i}. {result['source']} (Relevance: {result['relevance_score']:.2%})")
                rag_context += f"\n- {result['content'][:200]}..."
        else:
            print("📭 No prior knowledge found - will research from scratch")
        
        # PHASE 2: Initialize Agents - USING CORRECT METHOD NAMES
        print("\n🤖 PHASE 2: Initializing Agents...")
        
        controller = self.agents.controller_agent()
        researcher = self.agents.research_specialist()  # Correct!
        writer = self.agents.writing_specialist()       # Correct! (was writing_specialist not content_writer)
        editor = self.agents.editor_agent()             # Correct! (was editor_agent not editor)
        
        # PHASE 3: Create Tasks with Limits
        print("\n📋 PHASE 3: Creating Limited Tasks...")
        
        # Task 1: Limited Research with RAG context
        research_task = Task(
            description=f"""
            Research '{topic}' for {audience} audience.
            
            EXISTING KNOWLEDGE FROM DATABASE:
            {rag_context[:500] if rag_context else 'No prior knowledge available'}
            
            STRICT REQUIREMENTS:
            - MAXIMUM 3 search iterations
            - Use only TOP 5 sources
            - Focus on NEW information not in existing knowledge
            - Output: {self.max_research_words} words MAXIMUM
            - Include source citations
            - STOP after finding sufficient information
            
            DO NOT continue researching indefinitely!
            """,
            agent=researcher,
            expected_output=f"Concise research report ({self.max_research_words} words max)"
        )
        
        # Task 2: Writing with strict limit
        writing_task = Task(
            description=f"""
            Write an article about '{topic}' for {audience} audience.
            
            Use the research provided by the research agent.
            
            STRICT REQUIREMENTS:
            - MAXIMUM {self.max_article_words} words
            - Structure:
              * Introduction: 150-200 words
              * Body: 3 sections, 250-300 words each
              * Conclusion: 150-200 words
            - Clear, engaging, informative style
            - MUST STOP at {self.max_article_words} words
            
            OUTPUT ONLY the article text, no commentary.
            """,
            agent=writer,
            expected_output=f"Complete article ({self.max_article_words} words max)"
        )
        
        # Task 3: Quick final edit
        edit_task = Task(
            description=f"""
            Quickly polish the article about '{topic}'.
            
            Tasks:
            - Fix any grammar/spelling errors
            - Ensure smooth flow
            - Verify under {self.max_article_words} words
            - If over limit, TRIM to fit
            
            RETURN ONLY the final article text.
            """,
            agent=editor,
            expected_output="Final polished article"
        )
        
        # PHASE 4: Execute with Limits
        print("\n⚙️ PHASE 4: Executing Workflow (Limited)...")
        print(f"   Max iterations: {self.max_iterations}")
        print(f"   Max research: {self.max_research_words} words")
        print(f"   Max article: {self.max_article_words} words")
        
        crew = Crew(
            agents=[researcher, writer, editor],
            tasks=[research_task, writing_task, edit_task],
            process=Process.sequential,
            verbose=True,
            memory=False,  # Disable to avoid path issues
            cache=False,    # Disable cache
            max_iter=self.max_iterations  # HARD LIMIT on iterations
        )
        
        try:
            print("\n🔄 Starting agent execution...")
            result = crew.kickoff()
            print("\n✅ Agents completed successfully!")
        except Exception as e:
            logger.error(f"Workflow error: {e}")
            result = f"Error occurred: {str(e)[:500]}"
        
        # PHASE 5: Save Output
        print("\n💾 PHASE 5: Saving Results...")
        output_path = self._save_output(topic, result, rag_context)
        
        # PHASE 6: Update RAG with new knowledge
        if result and len(str(result)) > 500:
            print("📝 Adding new knowledge to RAG database...")
            try:
                self.rag.add_document(
                    content=str(result),
                    metadata={"topic": topic, "date": datetime.now().isoformat()}
                )
                print("✅ Knowledge base updated")
            except Exception as e:
                logger.error(f"Failed to update RAG: {e}")
        
        print("\n" + "="*60)
        print("✅ WORKFLOW COMPLETE!")
        print("="*60)
        
        return result
    
    def _save_output(self, topic, result, rag_context):
        """Save output to file"""
        output_dir = Path("outputs")
        output_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_topic = topic.replace(' ', '_').replace('/', '_')
        filename = f"{safe_topic}_{timestamp}_integrated.md"
        filepath = output_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"# {topic}\n\n")
                f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"**Mode:** Integrated (RAG + Agents)\n")
                f.write(f"**Audience:** General\n\n")
                
                if rag_context:
                    f.write("## Knowledge Base Context Used\n\n")
                    f.write(rag_context[:500] + "...\n\n")
                
                f.write("## Final Article\n\n")
                f.write(str(result))
                
                # Add statistics
                word_count = len(str(result).split())
                f.write(f"\n\n---\n")
                f.write(f"**Statistics:**\n")
                f.write(f"- Word count: {word_count}\n")
                f.write(f"- Characters: {len(str(result))}\n")
            
            print(f"✅ Output saved to: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Failed to save output: {e}")
            return None


# Main execution
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Enhanced Research Writing Assistant')
    parser.add_argument('--topic', type=str, default='AI Benefits',
                      help='Topic to research and write about')
    parser.add_argument('--audience', type=str, default='general',
                      help='Target audience')
    
    args = parser.parse_args()
    
    print("="*60)
    print("🚀 ENHANCED AI RESEARCH & WRITING ASSISTANT")
    print("   (RAG + Agents Integration with Limits)")
    print("="*60)
    
    orchestrator = EnhancedOrchestrator()
    result = orchestrator.run_integrated_workflow(args.topic, args.audience)
    
    if result:
        print("\n📄 Preview of Final Output:")
        print("-"*40)
        preview = str(result)[:500]
        print(preview + "..." if len(str(result)) > 500 else preview)
        
        word_count = len(str(result).split())
        print(f"\n📊 Word count: {word_count}")
        if word_count <= 1200:
            print("✅ Within limit!")
        else:
            print("⚠️ Exceeded limit")