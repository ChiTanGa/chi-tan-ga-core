import logging
from fastapi import FastAPI
import api
from core import setup_logging
from core import settings

# Set up own logging (separated from uvicorn)
setup_logging()
logger = logging.getLogger(__name__)  # Use module-level logger

app = FastAPI()

app.include_router(api.backup_router, prefix="/backup")
# Add other services like this:
# app.include_router(items.router, prefix="/items")
# app.include_router(auth.router, prefix="/auth")

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting uvicorn fast api backend.. ")
    uvicorn.run(app, host="0.0.0.0", port=settings.fast_api_port)
