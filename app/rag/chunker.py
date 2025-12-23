import json
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter

class ManimChunker:
    def __init__(self, input_file="manim_docs/manim_docs.json", output_file="manim_docs/chunks.json"):
        self.input_file = input_file
        self.output_file = output_file
        
    def chunk_data(self):
        if not os.path.exists(self.input_file):
            print(f"Input file {self.input_file} not found.")
            return
            
        with open(self.input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        print(f"Loaded {len(data)} pages. Chunking...")
        
        # Splitter optimized for code/text
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", " ", ""]
        )
        
        chunks = []
        for page in data:
            url = page['url']
            text = page['text']
            code = page.get('code', [])
            
            # Combine text and code for context, or treat them differently
            # For now, let's chunk the full text content which hopefully contains the code
            # If code is separate, we might want to append it or chunk it separately
            
            # Simple strategy: Chunk the main text
            doc_chunks = splitter.create_documents([text], metadatas=[{"url": url}])
            
            for chunk in doc_chunks:
                chunks.append({
                    "text": chunk.page_content,
                    "metadata": chunk.metadata
                })
        
        print(f"Created {len(chunks)} chunks.")
        
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(chunks, f, indent=2)
            
        print(f"Saved chunks to {self.output_file}")

if __name__ == "__main__":
    chunker = ManimChunker()
    chunker.chunk_data()
