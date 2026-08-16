import os
import uuid
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

class VectorStoreManager:
    """
    Manages vector storage and retrieval for research sources.
    Defaults to ChromaDB (local persistence), with Pinecone fallback if VECTOR_DB=pinecone.
    """

    def __init__(self, collection_name: str = "research_sources"):
        self.vector_db_type = os.getenv("VECTOR_DB", "chroma").lower()
        self.collection_name = collection_name
        self.memory_store = []
        self._init_db()

    def _init_db(self):
        if self.vector_db_type == "pinecone":
            self._init_pinecone()
        else:
            self._init_chroma()

    def _init_chroma(self):
        try:
            import chromadb
            persist_dir = os.path.join(os.getcwd(), "chroma_db_data")
            os.makedirs(persist_dir, exist_ok=True)
            self.client = chromadb.PersistentClient(path=persist_dir)
            self.collection = self.client.get_or_create_collection(name=self.collection_name)
            self.has_chroma = True
        except Exception as e:
            print(f"[VectorStore] ChromaDB init error: {e}. Using in-memory fallback store.")
            self.has_chroma = False

    def _init_pinecone(self):
        api_key = os.getenv("PINECONE_API_KEY")
        if not api_key:
            print("[VectorStore] Pinecone API key missing, falling back to ChromaDB")
            self.vector_db_type = "chroma"
            self._init_chroma()
            return
        
        try:
            from pinecone import Pinecone, ServerlessSpec
            pc = Pinecone(api_key=api_key)
            self.pc = pc
            self.index_name = self.collection_name.replace("_", "-")
            if self.index_name not in [idx.name for idx in pc.list_indexes()]:
                pc.create_index(
                    name=self.index_name,
                    dimension=384,
                    metric="cosine",
                    spec=ServerlessSpec(cloud="aws", region="us-east-1")
                )
            self.index = pc.Index(self.index_name)
        except Exception as e:
            print(f"[VectorStore] Failed to initialize Pinecone: {e}. Falling back to ChromaDB.")
            self.vector_db_type = "chroma"
            self._init_chroma()

    def add_documents(self, documents: List[Dict[str, Any]]) -> int:
        if not documents:
            return 0

        ids = [str(uuid.uuid4()) for _ in documents]
        texts = [doc.get("content", "") for doc in documents]
        metadatas = [
            {
                "source_id": str(doc.get("source_id", "")),
                "title": str(doc.get("title", ""))[:200],
                "url": str(doc.get("url", "")),
                "subtopic": str(doc.get("subtopic", "")),
                "snippet": str(doc.get("content", ""))[:300]
            }
            for doc in documents
        ]

        if getattr(self, "has_chroma", False):
            self.collection.add(
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
        else:
            for text, meta in zip(texts, metadatas):
                self.memory_store.append({"content": text, "metadata": meta})

        return len(documents)

    def similarity_search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        if getattr(self, "has_chroma", False):
            results = self.collection.query(
                query_texts=[query],
                n_results=min(top_k, self.collection.count() or 1)
            )
            
            output = []
            if results and results.get("documents") and results["documents"][0]:
                docs = results["documents"][0]
                metas = results["metadatas"][0] if results.get("metadatas") else [{}] * len(docs)
                distances = results["distances"][0] if results.get("distances") else [0.0] * len(docs)
                
                for doc, meta, dist in zip(docs, metas, distances):
                    output.append({
                        "content": doc,
                        "metadata": meta,
                        "distance": dist,
                        "similarity_score": round(max(0.0, 1.0 - (dist if dist is not None else 0.5)), 2)
                    })
            return output
        else:
            # Fallback keyword match in memory
            output = []
            q_words = set(query.lower().split())
            for item in self.memory_store:
                match_count = sum(1 for w in q_words if w in item["content"].lower())
                output.append({
                    "content": item["content"],
                    "metadata": item["metadata"],
                    "distance": 0.5,
                    "similarity_score": round(min(1.0, 0.3 + (match_count * 0.15)), 2)
                })
            output.sort(key=lambda x: x["similarity_score"], reverse=True)
            return output[:top_k]

    def clear(self):
        if getattr(self, "has_chroma", False):
            try:
                self.client.delete_collection(self.collection_name)
            except Exception:
                pass
            self.collection = self.client.get_or_create_collection(name=self.collection_name)
        else:
            self.memory_store = []
