import logging
from langgraph.checkpoint.redis import RedisSaver
from langgraph.checkpoint.memory import MemorySaver
from config import settings

logger = logging.getLogger("enterprise_agent.memory.short_term")

def get_checkpointer():
    """
    Initializes and returns the LangGraph checkpointer.
    Attempts to connect to Redis via REDIS_URL first.
    If Redis is not available or connection fails, falls back to MemorySaver 
    for easy local prototyping and robustness.
    
    Returns:
        BaseCheckpointSaver: The configured checkpointer.
    """
    if not settings.REDIS_URL:
        logger.warning("REDIS_URL environment variable is empty. Falling back to MemorySaver.")
        return MemorySaver()
        
    try:
        # Use the constructor directly (from_conn_string is a context manager
        # meant for short-lived usage; the constructor is better for long-lived apps)
        checkpointer = RedisSaver(redis_url=settings.REDIS_URL)
        logger.info(f"Initialized RedisSaver successfully with connection: {settings.REDIS_URL}")
        return checkpointer
    except Exception as e:
        logger.warning(
            f"Could not connect to Redis at {settings.REDIS_URL}. "
            f"Falling back to MemorySaver. Error: {str(e)}"
        )
        return MemorySaver()
