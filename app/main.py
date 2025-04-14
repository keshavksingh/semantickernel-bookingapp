from fastapi import FastAPI
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi.extension import _rate_limit_exceeded_handler
from routes import assistant
from dotenv import load_dotenv
import logging

load_dotenv()

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address, default_limits=["1000/second"])

# Create FastAPI app
app = FastAPI(
    title="Semantic Kernel Booking Assistant",
    description="Natural language booking assistant with context memory, planning, and Azure integration",
    version="1.0.0"
)

# Add rate limiting middleware
app.add_middleware(SlowAPIMiddleware)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Include API routes
app.include_router(assistant.router, prefix="/api")

# Basic health check route
@app.get("/")
def read_root():
    return {"status": "ok", "message": "Booking Assistant is running"}

# Optional: startup logging
@app.on_event("startup")
async def startup_event():
    logging.info("Booking Assistant API started.")
