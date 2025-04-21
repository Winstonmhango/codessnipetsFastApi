import uvicorn
import os
from app.core.config import settings

if __name__ == "__main__":
    # Get PORT from environment or use the default from settings
    port_str = os.getenv("PORT")
    port = int(port_str) if port_str else settings.PORT

    # Determine if we should enable reload based on environment
    reload = os.getenv("ENVIRONMENT") != "production"

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=reload,
        log_level="info"
    )
