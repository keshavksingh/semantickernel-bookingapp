import redis.asyncio as redis
from semantic_kernel.memory.memory_store_base import MemoryStoreBase
from semantic_kernel.memory.memory_record import MemoryRecord
import json
from typing import Optional
import os

class RedisMemoryStore(MemoryStoreBase):
    def __init__(self, redis_url=os.getenv("REDIS_URL"), ttl_seconds: int = 3600):
        self.redis_client = redis.from_url(redis_url)
        self.ttl = ttl_seconds  # Time to live for keys in seconds

    async def save(self, collection: str, key: str, record: MemoryRecord) -> None:
        full_key = f"{collection}:{key}"
        value = json.dumps({
            "text": record.text,
            "description": record.description,
            "additional_metadata": record.additional_metadata
        })
        await self.redis_client.set(full_key, value, ex=self.ttl)

    async def get(self, collection: str, key: str) -> Optional[MemoryRecord]:
        full_key = f"{collection}:{key}"
        value = await self.redis_client.get(full_key)
        if value is None:
            return None
        data = json.loads(value)
        return MemoryRecord(
            text=data["text"],
            description=data.get("description", ""),
            additional_metadata=data.get("additional_metadata", "")
        )

    async def remove(self, collection: str, key: str) -> None:
        full_key = f"{collection}:{key}"
        await self.redis_client.delete(full_key)
    
    async def append_conversation(self, customer_id: str, message: str):
        key = f"conversation:{customer_id}"
        await self.redis_client.rpush(key, message)
        await self.redis_client.expire(key, self.ttl)

    async def get_conversation_history(self, customer_id: str) -> list[str]:
        key = f"conversation:{customer_id}"
        return await self.redis_client.lrange(key, 0, -1)

    # --- Stub implementations for required abstract methods ---
    async def create_collection(self, collection_name: str) -> None:
        pass

    async def delete_collection(self, collection_name: str) -> None:
        pass

    async def does_collection_exist(self, collection_name: str) -> bool:
        return True

    async def get_collections(self) -> list[str]:
        return []

    async def get_nearest_match(self, collection: str, query: str, min_relevance_score: float = 0.0) -> Optional[MemoryRecord]:
        return None

    async def get_nearest_matches(self, collection: str, query: str, limit: int = 1, min_relevance_score: float = 0.0) -> list[MemoryRecord]:
        return []

    async def upsert(self, collection: str, record: MemoryRecord) -> None:
        pass

    async def upsert_batch(self, collection: str, records: list[MemoryRecord]) -> None:
        pass

    async def get_batch(self, collection: str, keys: list[str]) -> list[Optional[MemoryRecord]]:
        return [await self.get(collection, key) for key in keys]

    async def remove_batch(self, collection: str, keys: list[str]) -> None:
        await self.redis_client.delete(*[f"{collection}:{key}" for key in keys])
