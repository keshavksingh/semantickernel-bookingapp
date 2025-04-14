import os
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from services.redis_memory_store import RedisMemoryStore
from semantic_kernel.memory.memory_store_base import MemoryStoreBase
from plugins.booking_plugin import create_booking_plugin

# Initialize the Kernel
sk_kernel = Kernel()

# Register OpenAI Chat Completion service
api_key = os.getenv("OPENAI_API_KEY")
sk_kernel.add_service(OpenAIChatCompletion(ai_model_id="gpt-4o-mini-2024-07-18", api_key=api_key))

# Initialize Redis memory store
redis_memory_store = RedisMemoryStore(redis_url=os.getenv("REDIS_URL"))

# Load and add BookingPlugin
booking_plugin = create_booking_plugin()
sk_kernel.add_plugin(booking_plugin, plugin_name="BookingPlugin")
