"""
Text Splitter - Divide documentos em chunks
"""

from typing import List
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


class DocumentSplitter:
    """Divide documentos em chunks para embedding"""
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ".", " ", ""]
        )
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """Divide lista de documentos em chunks menores"""
        chunks = self.splitter.split_documents(documents)
        print(f"✅ Created {len(chunks)} chunks from {len(documents)} documents")
        return chunks


if __name__ == "__main__":
    from document_loader import KnowledgeBaseLoader
    
    loader = KnowledgeBaseLoader()
    docs = loader.load_documents()
    
    splitter = DocumentSplitter()
    chunks = splitter.split_documents(docs)
    
    print(f"\nExample chunk:")
    print(f"Content: {chunks[0].page_content[:200]}...")
    print(f"Metadata: {chunks[0].metadata}")