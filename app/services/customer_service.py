from azure.cosmos import CosmosClient
from services.redis_memory_store import RedisMemoryStore
from semantic_kernel.memory.memory_record import MemoryRecord
import os

class CustomerService:
    def __init__(self):
        self.client = CosmosClient.from_connection_string(os.getenv("COSMOS_CONNECTION_STRING"))
        self.database = self.client.get_database_client(os.getenv("COSMOS_DB_NAME"))
        self.container = self.database.get_container_client("customer")
        self.redis = RedisMemoryStore(redis_url=os.getenv("REDIS_URL"))

    async def get_customer_id_by_name(self, customer_name: str) -> str:
        
        query = f"SELECT c.customerId FROM c WHERE c.customerName = '{customer_name}'"
        items = list(self.container.query_items(query=query, enable_cross_partition_query=True))
        if not items:
            return -1

        customer_id = items[0]["customerId"]

        return customer_id
