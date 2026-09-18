import chromadb, logging
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

VECTOR_DB_DIR = "vector_db"
COLLECTION_NAME = "tourism"
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"


class Retriever:
    def __init__(
        self,
        vector_db_dir: str = VECTOR_DB_DIR,
        collection_name: str = COLLECTION_NAME,
        embedding_model: str = EMBEDDING_MODEL,
    ):
        self.client = chromadb.PersistentClient(path=vector_db_dir)

        self.collection = self.client.get_collection(
            name=collection_name
        )

        self.embedding_model = SentenceTransformer(
            embedding_model,
            local_files_only=True,
        )

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        destination: str | None = None,
    ):

        logger.debug("in retrieve method")
        query_embedding = self.embedding_model.encode(
            query,
            show_progress_bar=False,
            )

        query_params = {
            "query_embeddings": [query_embedding.tolist()],
            "n_results": top_k,
        }

        logger.debug(
            "Query: %s",
            query,
        )

        logger.debug(
            "Top K: %d",
            top_k,
        )

        logger.debug(
            "Destination filter: %s",
            destination,
        )

        if destination:
            query_params["where"] = {
                "destination": destination
            }

        results = self.collection.query(**query_params)

        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]

        retrieved_documents = []

        for document, metadata, distance in zip(
            documents,
            metadatas,
            distances,
        ):
            retrieved_documents.append({
                "text": document,
                "source": metadata["source"],
                "page": metadata["page"],
                "destination": metadata["destination"],
                "distance": distance,
            })

        logger.debug(
            "Retrieved %d documents",
            len(retrieved_documents),
        )

        return retrieved_documents

# can be removed.
# if __name__ == "__main__":
#     retriever = Retriever()

#     query = input("Ask about Singapore: ")

#     results = retriever.retrieve(
#         query=query,
#         top_k=5,
#         destination="Singapore",
#     )

#     for i, result in enumerate(results):
#         print("\n" + "=" * 60)
#         print(f"Result: {i + 1}")
#         print(f"Destination: {result['destination']}")
#         print(f"Source: {result['source']}")
#         print(f"Page: {result['page']}")
#         print(f"Distance: {result['distance']}")
#         print("\nText:")
#         print(result["text"])