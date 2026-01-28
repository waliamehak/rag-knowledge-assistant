from openai import OpenAI
import os
from dotenv import load_dotenv


load_dotenv

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_embedding(text):
    # Generate embedding vector for text
    response = client.embeddings.create(model="text-embedding-3-small", input=text)
    return response.data[0].embedding


def generate_answer(query, context_chunks):
    # Generate answer using GPT-4 with context
    context = "\n\n".join(context_chunks)

    prompt = f"""Answer the question based on the context below. If the answer is not in the context, say "I cannot answer based on the provided documents."

Context:
{context}

Question: {query}

Answer:"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that answers questions based on provided documents.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens=500,
    )

    return response.choices[0].message.content
