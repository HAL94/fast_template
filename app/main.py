
import uvicorn
from app.core.config import settings

def run():
    uvicorn.run("app.core.setup:app", host=settings.HOST, port=settings.APP_PORT, reload=True)


if __name__ == "__main__":
    run()
