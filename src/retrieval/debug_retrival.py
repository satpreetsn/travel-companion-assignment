import chromadb

client = chromadb.PersistentClient(path="vector_db")
collection = client.get_collection("tourism")

results = collection.get(
    where={"source": "Singapore.pdf"},
    include=["documents", "metadatas"]
)

for document, metadata in zip(
    results["documents"],
    results["metadatas"]
):
    if "colonial core" in document.lower():
        print("=" * 60)
        print(metadata)
        print(document)