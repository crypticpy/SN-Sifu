"""
cosmos_db_manager.py

This module provides a class for managing operations with Azure Cosmos DB.
It handles connections, CRUD operations, and query execution for KB articles and tickets.

Author: Principal Python Engineer
Date: 2024-07-14
"""

import logging
from typing import List, Dict, Any, Optional
from azure.cosmos import CosmosClient, PartitionKey, exceptions
from azure.cosmos.aio import CosmosClient as AsyncCosmosClient
from azure.cosmos.aio import ContainerProxy
from app.config import Config

logger = logging.getLogger(__name__)


class CosmosDBManager:
    def __init__(self, config: Config):
        self.config = config
        self.client = CosmosClient(self.config.COSMOS_ENDPOINT, self.config.COSMOS_KEY)
        self.database = self.client.get_database_client(self.config.COSMOS_DATABASE)
        self.container = self.database.get_container_client(self.config.COSMOS_CONTAINER)
        self.async_client = None
        self.async_database = None
        self.async_container = None

    async def initialize_async(self):
        """Initialize async client for use in async methods."""
        self.async_client = AsyncCosmosClient(self.config.COSMOS_ENDPOINT, self.config.COSMOS_KEY)
        self.async_database = self.async_client.get_database_client(self.config.COSMOS_DATABASE)
        self.async_container = self.async_database.get_container_client(self.config.COSMOS_CONTAINER)

    async def close_async(self):
        """Close the async client."""
        if self.async_client:
            await self.async_client.close()

    async def create_container_if_not_exists(self):
        """Create the container if it doesn't exist."""
        try:
            await self.async_database.create_container(
                id=self.config.COSMOS_CONTAINER,
                partition_key=PartitionKey(path="/id")
            )
            logger.info(f"Container '{self.config.COSMOS_CONTAINER}' created successfully.")
        except exceptions.CosmosResourceExistsError:
            logger.info(f"Container '{self.config.COSMOS_CONTAINER}' already exists.")
        except Exception as e:
            logger.error(f"Error creating container: {str(e)}")
            raise

    async def upsert_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Upsert an item (KB article or ticket) into the Cosmos DB container.
        """
        try:
            result = await self.async_container.upsert_item(item)
            logger.info(f"Item with id '{item.get('id')}' upserted successfully.")
            return result
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Failed to upsert item: {str(e)}")
            raise

    async def get_item(self, item_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve an item by its ID.
        """
        try:
            item = await self.async_container.read_item(item=item_id, partition_key=item_id)
            return item
        except exceptions.CosmosResourceNotFoundError:
            logger.warning(f"Item with id '{item_id}' not found.")
            return None
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Failed to retrieve item: {str(e)}")
            raise

    async def delete_item(self, item_id: str) -> None:
        """
        Delete an item by its ID.
        """
        try:
            await self.async_container.delete_item(item=item_id, partition_key=item_id)
            logger.info(f"Item with id '{item_id}' deleted successfully.")
        except exceptions.CosmosResourceNotFoundError:
            logger.warning(f"Item with id '{item_id}' not found for deletion.")
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Failed to delete item: {str(e)}")
            raise

    async def query_items(self, query: str, parameters: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """
        Execute a query against the Cosmos DB container.
        """
        try:
            results = []
            async for item in self.async_container.query_items(
                    query=query,
                    parameters=parameters,
                    enable_cross_partition_query=True
            ):
                results.append(item)
            return results
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Failed to execute query: {str(e)}")
            raise

    async def get_items_by_type(self, item_type: str) -> List[Dict[str, Any]]:
        """
        Retrieve items by their type (e.g., 'kb_article' or 'ticket').
        """
        query = "SELECT * FROM c WHERE c.type = @type"
        parameters = [{"name": "@type", "value": item_type}]
        return await self.query_items(query, parameters)

    async def get_item_count(self) -> int:
        """
        Get the total count of items in the container.
        """
        try:
            query = "SELECT VALUE COUNT(1) FROM c"
            results = await self.query_items(query)
            return results[0] if results else 0
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Failed to get item count: {str(e)}")
            raise

    async def bulk_upsert(self, items: List[Dict[str, Any]]) -> None:
        """
        Perform a bulk upsert operation for multiple items.
        """
        try:
            async with self.async_container.client.pipeline_executor(
                    retry_policy=self.async_container.client.retry_policy) as executor:
                tasks = [executor(self.async_container.upsert_item, body=item) for item in items]
                await executor.wait_all(tasks)
            logger.info(f"Bulk upsert of {len(items)} items completed successfully.")
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Failed to perform bulk upsert: {str(e)}")
            raise

    async def search_items(self, search_term: str, item_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search for items containing a specific term in their title, description, or content.
        Optionally filter by item type.
        """
        query = """
        SELECT * FROM c 
        WHERE (CONTAINS(LOWER(c.title), LOWER(@search_term)) 
            OR CONTAINS(LOWER(c.description), LOWER(@search_term))
            OR CONTAINS(LOWER(c.content), LOWER(@search_term)))
        """
        parameters = [{"name": "@search_term", "value": search_term.lower()}]

        if item_type:
            query += " AND c.type = @item_type"
            parameters.append({"name": "@item_type", "value": item_type})

        return await self.query_items(query, parameters)


# Example usage
if __name__ == "__main__":
    import asyncio
    from app.config import Config


    async def main():
        config = Config.from_env()
        cosmos_manager = CosmosDBManager(config)
        await cosmos_manager.initialize_async()

        # Example: Create container
        await cosmos_manager.create_container_if_not_exists()

        # Example: Upsert an item
        sample_item = {
            "id": "KB001",
            "type": "kb_article",
            "title": "Sample KB Article",
            "content": "This is a sample KB article content.",
            "created_at": "2024-07-14T00:00:00Z"
        }
        await cosmos_manager.upsert_item(sample_item)

        # Example: Retrieve the item
        retrieved_item = await cosmos_manager.get_item("KB001")
        print("Retrieved item:", retrieved_item)

        # Example: Search items
        search_results = await cosmos_manager.search_items("sample", "kb_article")
        print("Search results:", search_results)

        # Clean up
        await cosmos_manager.delete_item("KB001")
        await cosmos_manager.close_async()


    asyncio.run(main())
