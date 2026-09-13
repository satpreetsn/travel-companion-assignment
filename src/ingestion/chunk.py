from langchain_text_splitters import RecursiveCharacterTextSplitter


def chunk_documents(pages, source_name: str, destination: str):

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100
    )

    chunks = []

    chunk_index = 0

    for page in pages:

        page_chunks = splitter.split_text(
            page["text"]
        )

        for text in page_chunks:

            chunks.append({
                "id": f"{destination}::{source_name}::chunk_{chunk_index}",
                "text": text,
                "metadata": {
                    "source": source_name,
                    "page": page["metadata"]["page"],
                    "destination" : destination,
                },
            })

            chunk_index += 1

    return chunks