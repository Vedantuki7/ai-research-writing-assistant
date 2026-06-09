import os
from dotenv import load_dotenv
load_dotenv()

from src.rag_system import RAGKnowledgeBase

print("Testing RAG System...")
rag = RAGKnowledgeBase()
stats = rag.build_knowledge_base()
print(f"Results: {stats}")

# Test search
results = rag.retrieve("artificial intelligence", k=2)
print(f"Found {len(results)} results")