from pinecone import Pinecone, ServerlessSpec
import os

# Initialize Pinecone
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

INDEX_NAME = "rag-documents"


def create_index_if_not_exists():
    # Check if index exists
    if INDEX_NAME not in pc.list_indexes().names():
        pc.create_index(
            name=INDEX_NAME,
            dimension=1536,  # OpenAI embedding size
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws", region=os.getenv("PINECONE_ENVIRONMENT", "us-east-1")
            ),
        )
    return pc.Index(INDEX_NAME)


def store_chunks(chunks, filename):
    # Store document chunks in Pinecone with embeddings
    index = create_index_if_not_exists()

    vectors = []
    for i, chunk in enumerate(chunks):
        vector_id = f"{filename}_{i}"
        # We'll add embedding generation in next step
        # For now, just structure the data
        vectors.append(
            {
                "id": vector_id,
                "values": [],  # Will add embeddings next
                "metadata": {"text": chunk, "filename": filename, "chunk_index": i},
            }
        )

    return len(vectors)
