import chromadb
from chromadb.utils import embedding_functions
import json
import os

class ManimStore:
    def __init__(self, persist_directory="chroma_db", input_file="manim_docs/chunks.json"):
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(name="manim_docs")
        self.input_file = input_file
        
        # Use OpenAI Embeddings (requires OPENAI_API_KEY env var)
        # Or use default SentenceTransformer for local dev (no key needed)
        self.embedding_fn = embedding_functions.DefaultEmbeddingFunction()
        # To use OpenAI:
        # self.embedding_fn = embedding_functions.OpenAIEmbeddingFunction(
        #     api_key=os.environ.get("OPENAI_API_KEY"),
        #     model_name="text-embedding-3-small"
        # )

    def ingest(self):
        if not os.path.exists(self.input_file):
            print(f"Chunks file {self.input_file} not found.")
            return

        with open(self.input_file, 'r', encoding='utf-8') as f:
            chunks = json.load(f)
            
        print(f"Ingesting {len(chunks)} chunks into ChromaDB...")
        
        ids = [str(i) for i in range(len(chunks))]
        documents = [c['text'] for c in chunks]
        metadatas = [c['metadata'] for c in chunks]
        
        # Batch ingest to avoid limits
        batch_size = 100
        for i in range(0, len(chunks), batch_size):
            end = min(i + batch_size, len(chunks))
            print(f"Adding batch {i} to {end}")
            self.collection.add(
                ids=ids[i:end],
                documents=documents[i:end],
                metadatas=metadatas[i:end],
                # embeddings=self.embedding_fn(documents[i:end]) # Optional if using default
            )
            
        print("Ingestion complete.")

    def query(self, query_text, n_results=3):
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        return results

if __name__ == "__main__":
    store = ManimStore()
    store.ingest() # Run this once
    
    # Test query
    results = store.query("How to draw a circle?")
    if results['documents'] and results['documents'][0]:
        print("Test Query Results:", results['documents'][0][0])
    else:
        print("No results found.")
