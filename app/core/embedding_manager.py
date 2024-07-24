"""
embedding_manager.py

This module provides a class for managing text embedding operations using OpenAI's
text-embedding-3-large model. It handles the generation of embeddings for single
texts or batches of texts, and includes utility functions for working with embeddings.

Author: Principal Python Engineer
Date: 2024-07-14
"""

import logging
from typing import List, Dict, Any, Union
import numpy as np
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_random_exponential
from app.config import Config

logger = logging.getLogger(__name__)

class EmbeddingManager:
    def __init__(self, config: Config):
        self.config = config
        self.client = AsyncOpenAI(api_key=self.config.OPENAI_API_KEY)
        self.model = self.config.EMBEDDING_MODEL
        self.embedding_dimensions = 3072  # Default for text-embedding-3-large

    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(5))
    async def get_embedding(self, text: str) -> List[float]:
        """
        Generate an embedding for a single text string.

        Args:
        text: The input text to embed.

        Returns:
        A list of floats representing the embedding.
        """
        text = text.replace("\n", " ")
        try:
            response = await self.client.embeddings.create(
                input=[text],
                model=self.model
            )
            embedding = response.data[0].embedding
            logger.info(f"Generated embedding of length {len(embedding)}")
            return embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise

    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of text strings.

        Args:
        texts: A list of input texts to embed.

        Returns:
        A list of embeddings, where each embedding is a list of floats.
        """
        texts = [text.replace("\n", " ") for text in texts]
        try:
            response = await self.client.embeddings.create(
                input=texts,
                model=self.model
            )
            embeddings = [data.embedding for data in response.data]
            logger.info(f"Generated {len(embeddings)} embeddings of length {len(embeddings[0])}")
            return embeddings
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise

    async def get_embedding_batch(self, texts: List[str], batch_size: int = 100) -> List[List[float]]:
        """
        Generate embeddings for a large list of texts in batches.

        Args:
        texts: A list of input texts to embed.
        batch_size: The number of texts to process in each batch.

        Returns:
        A list of embeddings, where each embedding is a list of floats.
        """
        all_embeddings = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            batch_embeddings = await self.get_embeddings(batch)
            all_embeddings.extend(batch_embeddings)
            logger.info(f"Processed batch {i//batch_size + 1} of {(len(texts)-1)//batch_size + 1}")
        return all_embeddings

    @staticmethod
    def cosine_similarity(embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calculate the cosine similarity between two embeddings.

        Args:
        embedding1: The first embedding vector.
        embedding2: The second embedding vector.

        Returns:
        The cosine similarity as a float between -1 and 1.
        """
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

    def find_most_similar(self, query_embedding: List[float],
                          embeddings: List[List[float]],
                          top_k: int = 5) -> List[int]:
        """
        Find the indices of the most similar embeddings to a query embedding.

        Args:
        query_embedding: The query embedding to compare against.
        embeddings: A list of embeddings to search through.
        top_k: The number of most similar embeddings to return.

        Returns:
        A list of indices of the most similar embeddings.
        """
        similarities = [self.cosine_similarity(query_embedding, emb) for emb in embeddings]
        return sorted(range(len(similarities)), key=lambda i: similarities[i], reverse=True)[:top_k]

    async def search_similar_texts(self, query: str, texts: List[str], embeddings: List[List[float]], top_k: int = 5) -> List[Dict[str, Union[str, float]]]:
        """
        Search for texts similar to a query string.

        Args:
        query: The query string to search for.
        texts: A list of texts corresponding to the embeddings.
        embeddings: A list of embeddings corresponding to the texts.
        top_k: The number of most similar texts to return.

        Returns:
        A list of dictionaries containing the similar texts and their similarity scores.
        """
        query_embedding = await self.get_embedding(query)
        similar_indices = self.find_most_similar(query_embedding, embeddings, top_k)
        results = []
        for idx in similar_indices:
            similarity = self.cosine_similarity(query_embedding, embeddings[idx])
            results.append({
                "text": texts[idx],
                "similarity": similarity
            })
        return results

    def combine_embeddings(self, embeddings: List[List[float]]) -> List[float]:
        """
        Combine multiple embeddings into a single embedding by averaging.

        Args:
        embeddings: A list of embeddings to combine.

        Returns:
        A single combined embedding.
        """
        return list(np.mean(embeddings, axis=0))

# Example usage
if __name__ == "__main__":
    import asyncio
    from app.config import Config

    async def main():
        config = Config.from_env()
        embedding_manager = EmbeddingManager(config)

        # Example: Generate embedding for a single text
        text = "OpenAI's text-embedding-3-large model is powerful for various NLP tasks."
        embedding = await embedding_manager.get_embedding(text)
        print(f"Single embedding (first 5 dimensions): {embedding[:5]}")
        print(f"Embedding length: {len(embedding)}")

        # Example: Generate embeddings for multiple texts
        texts = [
            "The quick brown fox jumps over the lazy dog.",
            "OpenAI's GPT models have revolutionized natural language processing.",
            "Python is a versatile programming language used in data science and AI."
        ]
        embeddings = await embedding_manager.get_embeddings(texts)
        print(f"Number of embeddings: {len(embeddings)}")
        print(f"Each embedding length: {len(embeddings[0])}")

        # Example: Search similar texts
        query = "Artificial Intelligence and its applications in modern technology"
        similar_texts = await embedding_manager.search_similar_texts(query, texts, embeddings)
        for result in similar_texts:
            print(f"Similar text: {result['text']}")
            print(f"Similarity score: {result['similarity']:.4f}")

    asyncio.run(main())
