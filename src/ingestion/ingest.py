from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

from src.ingestion.load_pdf import load_pdf
from src.ingestion.chunk import chunk_documents
from src.ingestion.tracker import (
    calculate_file_hash,
    load_manifest,
    save_manifest
)


DATA_DIR = Path("data/raw")
VECTOR_DB_DIR = "vector_db"
COLLECTION_NAME = "tourism"
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"


def get_vector_collection():

    client = chromadb.PersistentClient(
        path=VECTOR_DB_DIR
    )

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME
    )

    return collection


def delete_source_chunks(collection, destination: str, source_name: str):
    """
    Delete every vector belonging to a particular PDF.
    """

    print(f"Deleting old chunks for: {source_name}")

    collection.delete(
        where={
            "$and": [
                {"destination": destination},
                {"source": source_name},
            ]
        }
    )

def ingest():
    collection = get_vector_collection()
    embedding_model = SentenceTransformer(EMBEDDING_MODEL)

    manifest = load_manifest()

    pdf_files = list(DATA_DIR.glob("*/*.pdf"))

    current_files = set()

    for pdf_path in pdf_files:
        destination = pdf_path.parent.name
        source_name = pdf_path.name

        relative_path = pdf_path.relative_to(DATA_DIR).as_posix()

        current_files.add(relative_path)

        file_hash = calculate_file_hash(pdf_path)

        previous_entry = manifest.get(relative_path)

        # File has not changed
        if previous_entry and previous_entry["hash"] == file_hash:
            print(f"[SKIP] {relative_path}")
            continue

        # New or changed file
        if previous_entry:
            print(f"[UPDATE] {relative_path}")

            delete_source_chunks(
                collection,
                destination,
                source_name,
            )
        else:
            print(f"[NEW] {relative_path}")

        pages = load_pdf(pdf_path)

        chunks = chunk_documents(
            pages,
            source_name,
            destination,
        )

        if not chunks:
            print(f"[WARNING] No text found in {relative_path}")
            continue

        texts = [chunk["text"] for chunk in chunks]
        ids = [chunk["id"] for chunk in chunks]
        metadatas = [chunk["metadata"] for chunk in chunks]

        embeddings = embedding_model.encode(
            texts,
            show_progress_bar=True,
        )

        collection.add(
            ids=ids,
            documents=texts,
            metadatas=metadatas,
            embeddings=embeddings.tolist(),
        )

        # Only update manifest after successful ingestion
        manifest[relative_path] = {
            "hash": file_hash
        }

        save_manifest(manifest)

        print(
            f"[DONE] {relative_path} "
            f"({len(chunks)} chunks)"
        )

    # Detect deleted PDFs
    tracked_files = set(manifest.keys())

    deleted_files = tracked_files - current_files

    for relative_path in deleted_files:
        print(f"[DELETE] {relative_path}")

        destination, source_name = relative_path.split("/", 1)

        delete_source_chunks(
            collection,
            destination,
            source_name,
        )

        del manifest[relative_path]

    save_manifest(manifest)

    print("\nIngestion complete.")


if __name__ == "__main__":
    ingest()