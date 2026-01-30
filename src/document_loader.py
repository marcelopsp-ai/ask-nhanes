"""
Document Loader - Carrega documentos da Knowledge Base
"""

from pathlib import Path
from typing import List
from langchain_core.documents import Document


class KnowledgeBaseLoader:
    """Carrega documentos .txt da knowledge base"""
    
    def __init__(self, knowledge_base_path: str = "data/knowledge_base"):
        self.kb_path = Path(knowledge_base_path)
    
    def load_documents(self) -> List[Document]:
        """Carrega todos os .txt e retorna lista de Documents"""
        documents = []
        
        for txt_file in self.kb_path.rglob("*.txt"):
            try:
                content = txt_file.read_text(encoding='utf-8')
                
                # Extrair source da primeira linha se existir
                lines = content.split('\n')
                source = txt_file.name
                if lines[0].startswith('Source:'):
                    source = lines[0].replace('Source:', '').strip()
                
                doc = Document(
                    page_content=content,
                    metadata={
                        "source": source,
                        "file": str(txt_file),
                        "category": txt_file.parent.name
                    }
                )
                documents.append(doc)
                
            except Exception as e:
                print(f"⚠️ Error loading {txt_file}: {e}")
        
        print(f"✅ Loaded {len(documents)} documents")
        return documents


if __name__ == "__main__":
    loader = KnowledgeBaseLoader()
    docs = loader.load_documents()
    for doc in docs[:3]:
        print(f"- {doc.metadata['file']}: {len(doc.page_content)} chars")