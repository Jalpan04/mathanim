
import chromadb
from chromadb.utils import embedding_functions
import os

class SolutionMemory:
    def __init__(self, persist_directory="chroma_db", collection_name="proven_solutions"):
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(name=collection_name)
        
        # Use simple default embeddings (all-MiniLM-L6-v2) suitable for local use
        self.embedding_fn = embedding_functions.DefaultEmbeddingFunction()

    def save_experience(self, prompt: str, code: str):
        """
        Saves a 5-star solution to memory.
        """
        import uuid
        doc_id = str(uuid.uuid4())
        
        print(f"Memory: Memorizing solution for '{prompt}'...")
        
        # Check if already exists to avoid duplicates (naive check)
        results = self.collection.query(query_texts=[prompt], n_results=1)
        if results['documents'] and results['documents'][0]:
            # If very similar exists, maybe skip? For now, we just add.
            pass

        self.collection.add(
            ids=[doc_id],
            documents=[prompt], # We embed the Prompt
            metadatas=[{"code": code}] # We store Code in metadata
        )
        print("Memory: Solution memorized.")

    def recall_experience(self, prompt: str, threshold=0.3):
        """
        Checks if a similar problem has been solved before.
        Returns the code if found, else None.
        """
        print(f"Memory: Recalling experience for '{prompt}'...")
        results = self.collection.query(
            query_texts=[prompt], 
            n_results=1
        )
        
        if not results['documents'] or not results['documents'][0]:
            print("Memory: No match found.")
            return None
            
        distance = results['distances'][0][0]
        # ChromaDB Default distance is usually Cosine/L2. Lower is better.
        # Threshold needs tuning, but 0.3-0.5 is usually good for semantic similarity.
        print(f"Memory: Closest match distance: {distance}")
        
        if distance < threshold:
            cached_code = results['metadatas'][0][0]['code']
            print("Memory: proven solution found!")
            return cached_code
            
        return None
