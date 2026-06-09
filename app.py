"""
Web Interface for AI Research & Writing Assistant
Streamlit app for demonstration
"""

import streamlit as st
import os
from dotenv import load_dotenv
load_dotenv()

# Import your system
from src.orchestrator_enhanced import EnhancedOrchestrator

# Page config
st.set_page_config(
    page_title="AI Research Assistant",
    page_icon="🤖",
    layout="wide"
)

# Title and description
st.title("🤖 AI-Powered Research & Writing Assistant")
st.markdown("### Research Synthesis Tool with RAG + Multi-Agent System")

import json
from pathlib import Path

# Dynamic System Stats Calculation
active_agents_count = len(EnhancedOrchestrator.ACTIVE_AGENTS)

# Vector Chunks Count
metadata_path = Path("knowledge_base/vectors/metadata.json")
if metadata_path.exists():
    try:
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        chunks_count = str(metadata.get("num_documents", "Not built yet"))
    except Exception:
        chunks_count = "Error reading metadata"
else:
    chunks_count = "Not built yet"

# Document Count
docs_path = Path("knowledge_base/documents")
if docs_path.exists():
    documents_count = len(list(docs_path.glob("*.txt")))
else:
    documents_count = 0

# Sidebar with information
with st.sidebar:
    st.markdown("## 📊 System Components")
    st.markdown(f"""
    **Generative AI Technologies:**
    - ✅ Prompt Engineering ({active_agents_count} agents)
    - ✅ RAG Implementation 
    - ✅ Multi-Agent System
    
    **Technical Stack:**
    - LangChain for RAG
    - FAISS Vector Database
    - CrewAI Framework
    - OpenAI GPT-4
    
    **System Stats:**
    - {documents_count} Knowledge Documents
    - {chunks_count} Vector Chunks
    - {active_agents_count} Coordinated Agents
    """)

# Main interface
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### Generate Research Article")
    topic = st.text_input("Enter research topic:", placeholder="e.g., Benefits of AI in Healthcare")
    
    col1_1, col1_2 = st.columns(2)
    with col1_1:
        audience = st.selectbox("Target audience:", ["general", "technical", "academic"])
    with col1_2:
        max_words = st.slider("Max words:", 500, 1500, 1200)

with col2:
    st.markdown("### Quick Examples")
    if st.button("AI in Healthcare"):
        topic = "Benefits of AI in Healthcare"
    if st.button("Machine Learning"):
        topic = "Machine Learning Applications"
    if st.button("Climate Change"):
        topic = "AI Solutions for Climate Change"

# Generate button
if st.button("🚀 Generate Article", type="primary", use_container_width=True):
    if topic:
        with st.spinner("🔄 Researching and writing... (this takes 2-3 minutes)"):
            try:
                # Initialize system
                orchestrator = EnhancedOrchestrator()
                
                # Progress updates
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                status_text.text("📚 Checking knowledge base...")
                progress_bar.progress(20)
                
                # Run the system
                result = orchestrator.run_integrated_workflow(topic, audience)
                
                progress_bar.progress(100)
                status_text.text("✅ Complete!")
                
                # Display results
                st.success("Article generated successfully!")
                
                # Show article
                st.markdown("### 📄 Generated Article")
                st.markdown(result)
                
                # Statistics
                word_count = len(str(result).split())
                char_count = len(str(result))
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Words", word_count)
                col2.metric("Characters", char_count)
                col3.metric("Paragraphs", str(result).count('\n\n'))
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
    else:
        st.warning("Please enter a topic")

# Footer
st.markdown("---")
st.markdown("Built with LangChain, CrewAI, and OpenAI | Research Synthesis Tool")