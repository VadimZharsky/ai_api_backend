import logging

import uvicorn

from app.app_builder import AppBuilder
from app_config import app_settings

app = AppBuilder.build()

if __name__ == '__main__':
    uvicorn.run(
        app="main:app",
        host="0.0.0.0",
        port=app_settings.SERVER.PORT,
        reload=False,
        log_level=logging.INFO,
        timeout_keep_alive=60,
    )
