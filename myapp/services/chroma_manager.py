"""
ChromaDB Manager Module

Handles vector database operations for storing and searching standard clauses.
Uses ChromaDB for efficient semantic similarity search.
"""

import os
import logging
from django.conf import settings as django_settings

logger = logging.getLogger(__name__)

# Try to import chromadb, but gracefully handle if dependencies are missing
try:
    import chromadb
    CHROMADB_AVAILABLE = True
except ImportError as e:
    logger.warning(f"ChromaDB or its dependencies not available: {str(e)}")
    logger.warning("Clause similarity search will be disabled. Install with: pip install chromadb")
    CHROMADB_AVAILABLE = False


class ChromaManager:
    """
    Manages ChromaDB vector database for contract clause comparison.
    
    This class provides methods to:
    - Store standard clauses as vectors
    - Search for similar clauses using semantic similarity
    - Create and manage collections for different contract types
    
    The database persists on disk, so data is not lost between runs.
    """

    def __init__(self):
        """
        Initialize ChromaDB connection with persistent storage.
        
        Creates the chroma_data directory if it doesn't exist and
        initializes the ChromaDB client for vector storage and search.
        
        Storage location: Uses CHROMA_DATA_DIR from Django settings
        """
        self.available = False
        self.client = None
        
        if not CHROMADB_AVAILABLE:
            logger.warning("ChromaDB not available - clause similarity search disabled")
            logger.warning("To enable: pip install chromadb 'sentence-transformers[torch]'")
            return
        
        try:
            # Get persist directory from settings or use default
            persist_dir = getattr(
                django_settings,
                'CHROMA_DATA_DIR',
                os.path.join(
                    django_settings.BASE_DIR,
                    'chroma_data'
                )
            )
            
            # Create directory if it doesn't exist
            os.makedirs(persist_dir, exist_ok=True)
            
            # Initialize ChromaDB client with persistent storage using new API
            # Use PersistentClient for persistent storage (non-deprecated way)
            self.client = chromadb.PersistentClient(path=persist_dir)
            self.available = True
            
            logger.info(f"ChromaDB initialized with storage at: {persist_dir}")
            
        except Exception as e:
            logger.error(f"Error initializing ChromaDB: {str(e)}")
            logger.warning("ChromaDB initialization failed - clause similarity search disabled")
            self.available = False
            self.client = None

    def get_or_create_collection(self, collection_name: str):
        """
        Get existing collection or create new one if it doesn't exist.
        
        Collections are used to organize clauses by contract type and jurisdiction.
        For example: "service_agreement_india", "employment_india", "nda_india"
        
        Args:
            collection_name (str): Name of the collection
                Example: "service_agreement_india"
        
        Returns:
            chromadb.Collection: The collection object for adding/querying clauses
            None: If ChromaDB is not available
        
        Example:
            >>> manager = ChromaManager()
            >>> collection = manager.get_or_create_collection("service_agreement_india")
            >>> # Use collection to add or search clauses
        """
        if not self.available or self.client is None:
            logger.debug(f"ChromaDB not available - cannot create collection '{collection_name}'")
            return None
        
        try:
            collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}  # Use cosine similarity
            )
            logger.debug(f"Collection '{collection_name}' ready for use")
            return collection
            
        except Exception as e:
            logger.error(f"Error accessing collection '{collection_name}': {str(e)}")
            return None

    def add_standard_clauses(self, collection_name: str, clauses: list) -> None:
        """
        Add standard clauses to a ChromaDB collection.
        
        Each clause is stored as a vector along with metadata for later
        retrieval. The metadata helps identify the type and properties of
        the clause.
        
        Args:
            collection_name (str): Name of the collection
                Example: "service_agreement_india"
            clauses (list): List of clause dictionaries
                Each dict should have:
                {
                    "type": "Payment Terms",
                    "text": "The full text of the standard clause...",
                    "jurisdiction": "INDIA",
                    "contract_type": "SERVICE_AGREEMENT",
                    "recommendations": "Should specify 30+ day terms"
                }
        
        Returns:
            None
        
        Example:
            >>> manager = ChromaManager()
            >>> clauses = [
            ...     {
            ...         "type": "Payment Terms",
            ...         "text": "Payment shall be made within 30 days...",
            ...         "jurisdiction": "INDIA",
            ...         "contract_type": "SERVICE_AGREEMENT",
            ...         "recommendations": "Standard industry practice"
            ...     }
            ... ]
            >>> manager.add_standard_clauses("service_agreement_india", clauses)
        """
        if not self.available:
            logger.debug("ChromaDB not available - skipping clause storage")
            return
        
        try:
            collection = self.get_or_create_collection(collection_name)
            if collection is None:
                logger.warning(f"Could not get collection '{collection_name}'")
                return
            
            for i, clause in enumerate(clauses):
                # Create unique ID for this clause
                clause_id = f"{collection_name}_clause_{i}"
                
                # Extract text for vectorization
                clause_text = clause.get('text', '')
                
                # Prepare metadata
                metadata = {
                    'type': clause.get('type', ''),
                    'jurisdiction': clause.get('jurisdiction', ''),
                    'contract_type': clause.get('contract_type', ''),
                    'recommendations': clause.get('recommendations', ''),
                }
                
                # Add to ChromaDB
                collection.add(
                    ids=[clause_id],
                    documents=[clause_text],
                    metadatas=[metadata]
                )
            
            logger.info(
                f"Successfully added {len(clauses)} clauses to '{collection_name}'"
            )
            
        except Exception as e:
            logger.error(
                f"Error adding clauses to '{collection_name}': {str(e)}"
            )
            raise

    def search_similar_clauses(
        self,
        collection_name: str,
        query_text: str,
        top_k: int = 3
    ) -> dict:
        """
        Search for clauses similar to the given query text.
        
        Uses semantic similarity (cosine distance) to find standard clauses
        that are most similar to a clause found in the contract being analyzed.
        
        Args:
            collection_name (str): Name of the collection to search
                Example: "service_agreement_india"
            query_text (str): The clause text to search for similarities
                Example: "Payment due within 15 days of invoice"
            top_k (int): Number of similar results to return (default: 3)
        
        Returns:
            dict: Search results with format:
            {
                "ids": ["service_agreement_india_clause_1", "..."],
                "documents": ["Standard clause text...", "..."],
                "metadatas": [{"type": "Payment Terms", ...}, ...],
                "distances": [0.15, 0.25, ...]  # Lower = more similar
            }
            
            If error occurs, returns empty results (doesn't raise exception)
        
        Example:
            >>> manager = ChromaManager()
            >>> results = manager.search_similar_clauses(
            ...     "service_agreement_india",
            ...     "Payment due in 15 days",
            ...     top_k=3
            ... )
            >>> for i, doc in enumerate(results["documents"]):
            ...     similarity = results["distances"][i]
            ...     print(f"Match {i+1} (similarity: {similarity}): {doc[:50]}...")
        """
        if not self.available:
            logger.debug("ChromaDB not available - returning empty results")
            return {
                'ids': [],
                'documents': [],
                'metadatas': [],
                'distances': []
            }
        
        try:
            collection = self.get_or_create_collection(collection_name)
            if collection is None:
                logger.warning(f"Could not get collection '{collection_name}'")
                return {
                    'ids': [],
                    'documents': [],
                    'metadatas': [],
                    'distances': []
                }
            
            # Perform similarity search
            results = collection.query(
                query_texts=[query_text],
                n_results=top_k
            )
            
            logger.debug(
                f"Found {len(results['documents'][0])} similar clauses "
                f"in '{collection_name}'"
            )
            
            # Format results for easier consumption
            if results and results['documents']:
                return {
                    'ids': results['ids'][0],
                    'documents': results['documents'][0],
                    'metadatas': results['metadatas'][0],
                    'distances': results['distances'][0] if 'distances' in results else []
                }
            else:
                return {
                    'ids': [],
                    'documents': [],
                    'metadatas': [],
                    'distances': []
                }
            
        except Exception as e:
            logger.warning(
                f"Error searching clauses in '{collection_name}': {str(e)}"
            )
            # Return empty results instead of failing
            return {
                'ids': [],
                'documents': [],
                'metadatas': [],
                'distances': []
            }

    def delete_collection(self, collection_name: str) -> None:
        """
        Delete a collection from ChromaDB.
        
        Useful for cleanup or resetting standard clauses.
        
        Args:
            collection_name (str): Name of the collection to delete
        
        Returns:
            None
        
        Example:
            >>> manager = ChromaManager()
            >>> manager.delete_collection("service_agreement_india")
        """
        if not self.available or self.client is None:
            logger.debug("ChromaDB not available - cannot delete collection")
            return
        
        try:
            self.client.delete_collection(name=collection_name)
            logger.info(f"Deleted collection: {collection_name}")
        except Exception as e:
            logger.warning(f"Error deleting collection '{collection_name}': {str(e)}")
