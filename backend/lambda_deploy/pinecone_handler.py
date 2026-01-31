from pinecone import Pinecone, ServerlessSpec
import os
from openai_handler import generate_embedding

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

        # Generate embedding for this chunk
        embedding = generate_embedding(chunk)

        vectors.append(
            {
                "id": vector_id,
                "values": embedding,
                "metadata": {"text": chunk, "filename": filename, "chunk_index": i},
            }
        )

    # Upload to Pinecone in batches
    if vectors:
        index.upsert(vectors=vectors)

    return len(vectors)


def search_similar_chunks(query, top_k=3):
    # Search for similar chunks using query embedding
    index = create_index_if_not_exists()

    # Generate embedding for query
    query_embedding = generate_embedding(query)

    # Search Pinecone
    results = index.query(vector=query_embedding, top_k=top_k, include_metadata=True)

    # Extract text chunks from results
    chunks = [match["metadata"]["text"] for match in results["matches"]]
    return chunks
