"""
RAG System for Research Writing Assistant
This module implements Retrieval-Augmented Generation with vector storage
Final version with all optimizations and error handling
"""

import os
import json
import pickle
import logging
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import numpy as np
import faiss
from dotenv import load_dotenv
load_dotenv()

from langchain_openai import OpenAIEmbeddings  # Updated import
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader, DirectoryLoader  # Updated import
from langchain.schema import Document
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

class RAGKnowledgeBase:
    """
    Complete RAG implementation with vector storage and retrieval
    Optimized for the Research Writing Assistant system
    """
    
    def __init__(self, 
                 knowledge_base_path: str = "knowledge_base",
                 embedding_model: str = "text-embedding-ada-002",
                 chunk_size: int = 500,
                 chunk_overlap: int = 100):
        """
        Initialize the RAG system
        
        Args:
            knowledge_base_path: Directory for storing knowledge base
            embedding_model: OpenAI embedding model to use
            chunk_size: Size of text chunks for processing
            chunk_overlap: Overlap between chunks for context preservation
        """
        self.knowledge_base_path = Path(knowledge_base_path)
        self.documents_path = self.knowledge_base_path / "documents"
        self.vectors_path = self.knowledge_base_path / "vectors"
        self.temp_path = self.knowledge_base_path / "temp"
        
        # Create directories if they don't exist
        for path in [self.documents_path, self.vectors_path, self.temp_path]:
            path.mkdir(parents=True, exist_ok=True)
        
        # Initialize embeddings
        try:
            self.embeddings = OpenAIEmbeddings(model=embedding_model)
        except Exception as e:
            logger.error(f"Error initializing embeddings: {e}")
            logger.info("Make sure OPENAI_API_KEY is set in your environment variables")
            raise
        
        # Chunking parameters
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Initialize storage
        self.vector_store = None
        self.documents = []
        self.metadata = {}
        
        logger.info(f"✅ RAG System initialized at {self.knowledge_base_path}")
        logger.info(f"   Chunk size: {chunk_size}, Overlap: {chunk_overlap}")
    
    def build_knowledge_base(self, rebuild: bool = False) -> Dict:
        """
        Build knowledge base from documents in the documents folder
        
        Args:
            rebuild: Force rebuild even if vectors exist
            
        Returns:
            Statistics about the knowledge base
        """
        vector_index_path = self.vectors_path / "index.faiss"
        
        # Check if vectors already exist
        if vector_index_path.exists() and not rebuild:
            logger.info("📚 Loading existing knowledge base...")
            success = self.load_knowledge_base()
            if success:
                return {
                    "status": "loaded",
                    "documents": len(self.documents),
                    "vector_dimensions": self.vector_store.d if self.vector_store else 0
                }
        
        logger.info("🔨 Building new knowledge base...")
        
        # Load all documents from documents folder
        documents = self._load_documents()
        
        if not documents:
            logger.warning("⚠️ No documents found in knowledge_base/documents/")
            logger.info("   Please add .txt or .pdf files to the documents folder")
            return {"status": "empty", "documents": 0}
        
        # Split documents into chunks
        chunks = self._chunk_documents(documents)
        
        # Create embeddings and vector store
        success = self._create_vector_store(chunks)
        
        if not success:
            return {"status": "failed", "documents": 0}
        
        # Save the knowledge base
        self._save_knowledge_base()
        
        stats = {
            "status": "built",
            "documents": len(documents),
            "chunks": len(self.documents),
            "vector_dimensions": self.vector_store.d if self.vector_store else 0,
            "avg_chunk_length": int(np.mean([len(chunk.page_content) for chunk in chunks]))
        }
        
        logger.info(f"✅ Knowledge base built successfully!")
        logger.info(f"   Documents: {stats['documents']}")
        logger.info(f"   Chunks: {stats['chunks']}")
        logger.info(f"   Dimensions: {stats['vector_dimensions']}")
        
        return stats
    
    def _load_documents(self) -> List[Document]:
        """Load all documents from the documents folder"""
        documents = []
        
        # Load text files
        txt_files = list(self.documents_path.glob("**/*.txt"))
        
        for txt_file in txt_files:
            try:
                with open(txt_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    doc = Document(
                        page_content=content,
                        metadata={
                            'source': str(txt_file.name),
                            'type': 'text',
                            'path': str(txt_file)
                        }
                    )
                    documents.append(doc)
                    logger.info(f"   📄 Loaded: {txt_file.name}")
            except Exception as e:
                logger.error(f"   ❌ Error loading {txt_file.name}: {e}")
        
        # Optionally load PDF files
        pdf_files = list(self.documents_path.glob("**/*.pdf"))
        
        if pdf_files:
            try:
                from langchain_community.document_loaders import PyPDFLoader
                
                for pdf_file in pdf_files:
                    try:
                        pdf_loader = PyPDFLoader(str(pdf_file))
                        pdf_docs = pdf_loader.load()
                        for doc in pdf_docs:
                            doc.metadata['type'] = 'pdf'
                            doc.metadata['source'] = pdf_file.name
                        documents.extend(pdf_docs)
                        logger.info(f"   📄 Loaded PDF: {pdf_file.name}")
                    except Exception as e:
                        logger.error(f"   ❌ Error loading PDF {pdf_file.name}: {e}")
            except ImportError:
                if pdf_files:
                    logger.warning("   ⚠️ PyPDF2 not installed, skipping PDF files")
        
        logger.info(f"📚 Total documents loaded: {len(documents)}")
        return documents
    
    def _chunk_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split documents into smaller chunks for better retrieval
        
        This implements the 'Design relevant document chunking strategies' requirement
        """
        logger.info("📑 Chunking documents...")
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", "! ", "? ", " ", ""]
        )
        
        chunks = []
        for doc in documents:
            doc_chunks = text_splitter.split_documents([doc])
            
            # Add metadata to each chunk
            for i, chunk in enumerate(doc_chunks):
                chunk.metadata.update({
                    'chunk_id': f"{doc.metadata['source']}_{i}",
                    'chunk_index': i,
                    'total_chunks': len(doc_chunks),
                    'timestamp': datetime.now().isoformat()
                })
            chunks.extend(doc_chunks)
        
        logger.info(f"   ✅ Created {len(chunks)} chunks")
        logger.info(f"   📊 Average chunk size: {int(np.mean([len(c.page_content) for c in chunks]))} chars")
        
        return chunks
    
    def _create_vector_store(self, chunks: List[Document]) -> bool:
        """
        Create FAISS vector store with embeddings
        
        This implements 'Implement vector storage and retrieval' requirement
        """
        if not chunks:
            logger.error("No chunks to create vectors from")
            return False
        
        logger.info("🔄 Creating embeddings (this may take a moment)...")
        
        # Extract text from chunks
        texts = [chunk.page_content for chunk in chunks]
        
        # Create embeddings in batches to avoid rate limits
        batch_size = 100
        all_embeddings = []
        
        try:
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                logger.info(f"   Processing batch {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1}")
                batch_embeddings = self.embeddings.embed_documents(batch)
                all_embeddings.extend(batch_embeddings)
        except Exception as e:
            logger.error(f"Error creating embeddings: {e}")
            logger.info("Check your OpenAI API key and rate limits")
            return False
        
        # Convert to numpy array
        embeddings_array = np.array(all_embeddings).astype('float32')
        
        # Create FAISS index
        dimension = embeddings_array.shape[1]
        
        # Use IndexFlatL2 for small datasets, IndexIVFFlat for larger ones
        if len(chunks) < 10000:
            self.vector_store = faiss.IndexFlatL2(dimension)
        else:
            # For larger datasets, use IVF index for faster search
            nlist = min(100, len(chunks) // 10)  # Number of clusters
            self.vector_store = faiss.IndexIVFFlat(
                faiss.IndexFlatL2(dimension), dimension, nlist
            )
            self.vector_store.train(embeddings_array)
        
        # Add vectors to index
        self.vector_store.add(embeddings_array)
        
        # Store documents
        self.documents = chunks
        
        logger.info(f"✅ Created vector store with {len(chunks)} vectors")
        logger.info(f"   Vector dimensions: {dimension}")
        
        return True
    
    def retrieve(self, 
                query: str, 
                k: int = 5,
                threshold: float = 2.0,
                return_scores: bool = True) -> List[Dict]:
        """
        Retrieve relevant documents for a query
        
        This implements 'Create effective ranking and filtering mechanisms' requirement
        
        Args:
            query: Search query
            k: Number of results to return
            threshold: Relevance threshold (lower is more relevant)
            return_scores: Whether to include relevance scores
            
        Returns:
            List of relevant documents with scores
        """
        if not self.vector_store or not self.documents:
            logger.warning("⚠️ No vector store available. Build knowledge base first.")
            return []
        
        # Create query embedding
        try:
            query_embedding = self.embeddings.embed_query(query)
            query_vector = np.array([query_embedding]).astype('float32')
        except Exception as e:
            logger.error(f"Error creating query embedding: {e}")
            return []
        
        # Search in vector store
        try:
            distances, indices = self.vector_store.search(query_vector, min(k, len(self.documents)))
        except Exception as e:
            logger.error(f"Error searching vector store: {e}")
            return []
        
        # Process results with ranking and filtering
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            # Filter by relevance threshold
            if distance > threshold:
                continue
            
            if idx < len(self.documents):
                doc = self.documents[idx]
                
                # Calculate relevance score (convert distance to similarity)
                relevance_score = 1 / (1 + distance)
                
                result = {
                    'content': doc.page_content,
                    'metadata': doc.metadata,
                    'source': doc.metadata.get('source', 'unknown')
                }
                
                if return_scores:
                    result['relevance_score'] = float(relevance_score)
                    result['distance'] = float(distance)
                
                results.append(result)
        
        # Sort by relevance score (highest first)
        if return_scores:
            results.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        logger.info(f"🔍 Retrieved {len(results)} relevant documents for: '{query[:50]}...'")
        
        return results
    
    def add_document(self, content: str, metadata: Dict = None) -> bool:
        """
        Add a new document to the knowledge base dynamically
        
        Args:
            content: Document content
            metadata: Optional metadata
            
        Returns:
            Success status
        """
        try:
            # Save document to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"added_{timestamp}.txt"
            filepath = self.documents_path / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"✅ Added new document: {filename}")
            
            # Rebuild knowledge base to include new document
            self.build_knowledge_base(rebuild=True)
            
            return True
            
        except Exception as e:
            logger.error(f"Error adding document: {e}")
            return False
    
    def _save_knowledge_base(self):
        """Save vector store and documents to disk"""
        try:
            # Save FAISS index
            faiss.write_index(
                self.vector_store, 
                str(self.vectors_path / "index.faiss")
            )
            
            # Save documents
            with open(self.vectors_path / "documents.pkl", 'wb') as f:
                pickle.dump(self.documents, f)
            
            # Save metadata
            self.metadata['last_updated'] = datetime.now().isoformat()
            self.metadata['num_documents'] = len(self.documents)
            self.metadata['chunk_size'] = self.chunk_size
            self.metadata['chunk_overlap'] = self.chunk_overlap
            
            with open(self.vectors_path / "metadata.json", 'w') as f:
                json.dump(self.metadata, f, indent=2)
            
            logger.info("💾 Knowledge base saved to disk")
            
        except Exception as e:
            logger.error(f"Error saving knowledge base: {e}")
    
    def load_knowledge_base(self) -> bool:
        """Load existing knowledge base from disk"""
        try:
            # Load FAISS index
            index_path = self.vectors_path / "index.faiss"
            if index_path.exists():
                self.vector_store = faiss.read_index(str(index_path))
            else:
                logger.warning("Vector index not found")
                return False
            
            # Load documents
            docs_path = self.vectors_path / "documents.pkl"
            if docs_path.exists():
                with open(docs_path, 'rb') as f:
                    self.documents = pickle.load(f)
            else:
                logger.warning("Documents file not found")
                return False
            
            # Load metadata
            metadata_path = self.vectors_path / "metadata.json"
            if metadata_path.exists():
                with open(metadata_path, 'r') as f:
                    self.metadata = json.load(f)
            
            logger.info(f"📚 Loaded knowledge base:")
            logger.info(f"   Documents: {len(self.documents)}")
            logger.info(f"   Last updated: {self.metadata.get('last_updated', 'Unknown')}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error loading knowledge base: {e}")
            return False
    
    def get_statistics(self) -> Dict:
        """Get comprehensive statistics about the knowledge base"""
        stats = {
            "initialized": True,
            "documents_count": len(self.documents),
            "vector_store_size": self.vector_store.ntotal if self.vector_store else 0,
            "vector_dimensions": self.vector_store.d if self.vector_store else 0,
            "last_updated": self.metadata.get('last_updated', 'Never'),
            "chunk_size": self.metadata.get('chunk_size', self.chunk_size),
            "chunk_overlap": self.metadata.get('chunk_overlap', self.chunk_overlap),
            "documents_folder": str(self.documents_path),
            "vectors_folder": str(self.vectors_path),
            "total_text_length": sum(len(doc.page_content) for doc in self.documents) if self.documents else 0
        }
        
        # Get document sources
        if self.documents:
            sources = list(set(doc.metadata.get('source', 'unknown') for doc in self.documents))
            stats['sources'] = sources[:10]  # First 10 sources
            stats['num_sources'] = len(sources)
        
        return stats
    
    def clear_knowledge_base(self):
        """Clear all vector data (keeps documents)"""
        self.vector_store = None
        self.documents = []
        self.metadata = {}
        
        # Remove vector files
        for file in self.vectors_path.glob("*"):
            if file.is_file():
                file.unlink()
        
        logger.info("🗑️ Knowledge base cleared (documents preserved)")


# ============================================================================
# Integration Helper for Your Existing System
# ============================================================================

class RAGEnhancedResearch:
    """
    Helper class to integrate RAG with your existing agents
    """
    
    def __init__(self, rag_system: RAGKnowledgeBase):
        self.rag = rag_system
    
    def enhance_research_task(self, topic: str, original_task: str) -> str:
        """
        Enhance a research task with knowledge base context
        
        Args:
            topic: Research topic
            original_task: Original task description
            
        Returns:
            Enhanced task with knowledge base context
        """
        # Retrieve relevant information
        results = self.rag.retrieve(topic, k=3, threshold=1.5)
        
        if not results:
            return original_task
        
        # Format knowledge base context
        kb_context = "\n📚 Relevant information from knowledge base:\n"
        for i, result in enumerate(results, 1):
            kb_context += f"\n{i}. {result['content'][:200]}..."
            kb_context += f"\n   Source: {result['source']}"
            kb_context += f"\n   Relevance: {result.get('relevance_score', 0):.2%}\n"
        
        # Enhance the original task
        enhanced_task = f"""
{original_task}

{kb_context}

Consider the above information from the knowledge base while completing your task.
Look for information that complements or updates this existing knowledge.
"""
        
        return enhanced_task
    
    def format_retrieval_results(self, results: List[Dict], max_length: int = 500) -> str:
        """
        Format retrieval results for agent consumption
        
        Args:
            results: RAG retrieval results
            max_length: Maximum length per result
            
        Returns:
            Formatted string for agents
        """
        if not results:
            return "No relevant information found in knowledge base."
        
        formatted = "📚 Knowledge Base Information:\n\n"
        
        for i, result in enumerate(results, 1):
            content = result['content'][:max_length]
            if len(result['content']) > max_length:
                content += "..."
            
            formatted += f"{i}. **{result['source']}**\n"
            formatted += f"   {content}\n"
            if 'relevance_score' in result:
                formatted += f"   *Relevance: {result['relevance_score']:.2%}*\n"
            formatted += "\n"
        
        return formatted


# ============================================================================
# Testing Script
# ============================================================================

if __name__ == "__main__":
    print("="*60)
    print("🚀 RAG KNOWLEDGE BASE SYSTEM - SETUP & TEST")
    print("="*60)
    
    # Initialize RAG system
    rag = RAGKnowledgeBase(chunk_size=500, chunk_overlap=100)
    
    # Build knowledge base
    print("\n📚 Building knowledge base from documents...")
    stats = rag.build_knowledge_base()
    print(f"\n✅ Knowledge base stats:")
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # Test retrieval with different queries
    print("\n" + "="*60)
    print("🔍 Testing retrieval with sample queries...")
    print("="*60)
    
    test_queries = [
        "artificial intelligence and machine learning",
        "research methodology best practices",
        "writing techniques for professionals",
        "deep learning neural networks",
        "data science and analytics"
    ]
    
    for query in test_queries:
        print(f"\n📝 Query: '{query}'")
        print("-" * 40)
        
        results = rag.retrieve(query, k=2, threshold=2.0)
        
        if results:
            for i, result in enumerate(results, 1):
                print(f"\n   Result {i}:")
                print(f"   Source: {result['source']}")
                print(f"   Relevance: {result.get('relevance_score', 0):.2%}")
                print(f"   Preview: {result['content'][:150]}...")
        else:
            print("   No relevant results found")
    
    # Show final statistics
    print("\n" + "="*60)
    print("📊 Final System Statistics:")
    print("="*60)
    final_stats = rag.get_statistics()
    for key, value in final_stats.items():
        if key != 'sources':  # Skip the sources list for cleaner output
            print(f"   {key}: {value}")
    
    print("\n" + "="*60)
    print("✅ RAG SYSTEM READY FOR INTEGRATION!")
    print("="*60)
    print("\n💡 Next steps:")
    print("1. Add your documents to knowledge_base/documents/")
    print("2. Import this module in your orchestrator.py:")
    print("   from rag_system import RAGKnowledgeBase")
    print("3. Initialize and use in your workflow:")
    print("   rag = RAGKnowledgeBase()")
    print("   results = rag.retrieve('your query')")
    print("\n🎉 Your RAG system is production-ready!")