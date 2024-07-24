"""
article_processor.py

This module provides a class for processing KB articles and ticket data.
It integrates the CosmosDBManager and EmbeddingManager to handle storage
and embedding generation for articles and tickets.

Author: Principal Python Engineer
Date: 2024-07-14
"""

import logging
from typing import List, Dict, Any, Optional
import pandas as pd
from datetime import datetime
from app.config import Config
from app.core.cosmos_db_manager import CosmosDBManager
from app.core.embedding_manager import EmbeddingManager

logger = logging.getLogger(__name__)


class ArticleProcessor:
    def __init__(self, config: Config):
        self.config = config
        self.cosmos_manager = CosmosDBManager(config)
        self.embedding_manager = EmbeddingManager(config)

    async def initialize(self):
        """Initialize async clients for CosmosDBManager and EmbeddingManager."""
        await self.cosmos_manager.initialize_async()

    async def close(self):
        """Close async clients."""
        await self.cosmos_manager.close_async()

    async def process_kb_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single KB article, ensuring uniqueness and proper versioning.

        Args:
        article: Dictionary containing KB article data

        Returns:
        Processed article with generated embedding
        """
        try:
            # Check if the article already exists
            existing_article = await self.cosmos_manager.get_item(article["KB Article #"])
            if existing_article:
                # Update the existing article with new information
                for key, value in article.items():
                    existing_article[key] = value
                article = existing_article
                article["Version"] = str(float(article["Version"]) + 0.1)  # Increment version
                logger.info(f"Updating existing KB article {article['KB Article #']} to version {article['Version']}")
            else:
                logger.info(f"Creating new KB article {article['KB Article #']}")

            # Generate embedding for the article content
            content = f"{article['Title']} {article['Introduction']} {article['Instructions']}"
            embedding = await self.embedding_manager.get_embedding(content)

            # Prepare article for storage
            processed_article = {
                "id": article["KB Article #"],
                "type": "kb_article",
                "version": article["Version"],
                "category": article["Category"],
                "title": article["Title"],
                "introduction": article["Introduction"],
                "instructions": article["Instructions"],
                "keywords": article["Keywords"],
                "updated": datetime.now().isoformat(),
                "embedding": embedding
            }

            # Store the article in Cosmos DB
            await self.cosmos_manager.upsert_item(processed_article)
            logger.info(f"Processed and stored KB article: {processed_article['id']}")

            return processed_article
        except Exception as e:
            logger.error(f"Error processing KB article: {str(e)}")
            raise

    async def process_ticket(self, ticket: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single ticket.

        Args:
        ticket: Dictionary containing ticket data

        Returns:
        Processed ticket with generated embedding
        """
        try:
            # Generate embedding for the ticket content
            content = f"{ticket['Description']} {ticket['Close Notes']} {ticket['summarize_ticket']}"
            embedding = await self.embedding_manager.get_embedding(content)

            # Prepare ticket for storage
            processed_ticket = {
                "id": f"{ticket['tracking_index']}_{datetime.now().isoformat()}",  # Ensure uniqueness
                "type": "ticket",
                "tracking_index": ticket["tracking_index"],
                "description": ticket["Description"],
                "close_notes": ticket["Close Notes"],
                "summary": ticket["summarize_ticket"],
                "ticket_quality": ticket["ticket_quality"],
                "user_proficiency": ticket["user_proficiency_level"],
                "potential_impact": ticket["potential_impact"],
                "resolution_appropriateness": ticket["resolution_appropriateness"],
                "potential_root_cause": ticket["potential_root_cause"],
                "embedding": embedding,
                "created_at": datetime.now().isoformat()
            }

            # Add optional fields if they exist
            optional_fields = [
                "summarize_ticket_explanation", "ticket_quality_explanation",
                "user_proficiency_level_explanation", "potential_impact_explanation",
                "resolution_appropriateness_explanation", "potential_root_cause_explanation"
            ]
            for field in optional_fields:
                if field in ticket:
                    processed_ticket[field] = ticket[field]

            # Store the ticket in Cosmos DB
            await self.cosmos_manager.upsert_item(processed_ticket)
            logger.info(f"Processed and stored ticket: {processed_ticket['id']}")

            return processed_ticket
        except Exception as e:
            logger.error(f"Error processing ticket: {str(e)}")
            raise

    async def process_dataframe(self, df: pd.DataFrame, item_type: str) -> List[Dict[str, Any]]:
        """
        Process a dataframe of KB articles or tickets.

        Args:
        df: DataFrame containing KB articles or tickets
        item_type: Either 'kb_article' or 'ticket'

        Returns:
        List of processed items
        """
        processed_items = []
        for _, row in df.iterrows():
            item = row.to_dict()
            if item_type == 'kb_article':
                processed_item = await self.process_kb_article(item)
            elif item_type == 'ticket':
                processed_item = await self.process_ticket(item)
            else:
                raise ValueError(f"Invalid item type: {item_type}")
            processed_items.append(processed_item)

        logger.info(f"Processed {len(processed_items)} items of type {item_type}")
        return processed_items

    async def search_similar_items(self, query: str, item_type: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for items similar to the query.

        Args:
        query: The search query
        item_type: Either 'kb_article' or 'ticket'
        top_k: Number of top results to return

        Returns:
        List of similar items
        """
        try:
            # Generate embedding for the query
            query_embedding = await self.embedding_manager.get_embedding(query)

            # Retrieve all items of the specified type
            items = await self.cosmos_manager.get_items_by_type(item_type)

            # Extract embeddings and texts
            embeddings = [item['embedding'] for item in items]
            texts = [item['title'] if item_type == 'kb_article' else item['description'] for item in items]

            # Find most similar items
            similar_indices = self.embedding_manager.find_most_similar(query_embedding, embeddings, top_k)

            # Prepare results
            results = []
            for idx in similar_indices:
                item = items[idx]
                similarity = self.embedding_manager.cosine_similarity(query_embedding, item['embedding'])
                results.append({
                    "id": item['id'],
                    "type": item_type,
                    "content": item['title'] if item_type == 'kb_article' else item['description'],
                    "similarity": similarity
                })

            return results
        except Exception as e:
            logger.error(f"Error searching similar items: {str(e)}")
            raise

    async def get_item_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the items in the database.

        Returns:
        Dictionary containing various statistics
        """
        try:
            kb_articles = await self.cosmos_manager.get_items_by_type('kb_article')
            tickets = await self.cosmos_manager.get_items_by_type('ticket')

            stats = {
                "total_kb_articles": len(kb_articles),
                "total_tickets": len(tickets),
                "kb_article_categories": {},
                "ticket_quality_distribution": {},
                "user_proficiency_distribution": {}
            }

            for article in kb_articles:
                category = article.get('category', 'Unknown')
                stats["kb_article_categories"][category] = stats["kb_article_categories"].get(category, 0) + 1

            for ticket in tickets:
                quality = ticket.get('ticket_quality', 'Unknown')
                proficiency = ticket.get('user_proficiency', 'Unknown')
                stats["ticket_quality_distribution"][quality] = stats["ticket_quality_distribution"].get(quality, 0) + 1
                stats["user_proficiency_distribution"][proficiency] = stats["user_proficiency_distribution"].get(
                    proficiency, 0) + 1

            return stats
        except Exception as e:
            logger.error(f"Error getting item statistics: {str(e)}")
            raise


# Example usage
if __name__ == "__main__":
    import asyncio
    from app.config import Config


    async def main():
        config = Config.from_env()
        processor = ArticleProcessor(config)
        await processor.initialize()

        # Example: Process a KB article
        kb_article = {
            "KB Article #": "KB001",
            "Version": "1.0",
            "Category": "Troubleshooting",
            "Title": "How to reset your password",
            "Introduction": "This article explains the process of resetting your password.",
            "Instructions": "1. Go to the login page. 2. Click on 'Forgot Password'. 3. Follow the prompts.",
            "Keywords": "password, reset, login"
        }
        processed_article = await processor.process_kb_article(kb_article)
        print("Processed KB Article:", processed_article['id'])

        # Example: Process a ticket
        ticket = {
            "tracking_index": "T001",
            "Description": "User unable to log in to the system",
            "Close Notes": "Guided user through password reset process",
            "summarize_ticket": "Password reset assistance provided",
            "ticket_quality": "Good",
            "user_proficiency_level": "Beginner",
            "potential_impact": "Low",
            "resolution_appropriateness": "Appropriate",
            "potential_root_cause": "Forgotten password"
        }
        processed_ticket = await processor.process_ticket(ticket)
        print("Processed Ticket:", processed_ticket['id'])

        # Example: Search similar items
        similar_items = await processor.search_similar_items("password reset", "kb_article", top_k=3)
        print("Similar KB Articles:")
        for item in similar_items:
            print(f"- {item['content']} (Similarity: {item['similarity']:.2f})")

        # Example: Get item statistics
        stats = await processor.get_item_statistics()
        print("Item Statistics:")
        print(f"Total KB Articles: {stats['total_kb_articles']}")
        print(f"Total Tickets: {stats['total_tickets']}")

        await processor.close()


    asyncio.run(main())