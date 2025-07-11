
import uvicorn
from app.core.setup import FastApp
from app.core.config import get_settings

settings = get_settings()
app = FastApp(settings=settings)


def run():
    uvicorn.run(app, host="localhost", port=8000)


if __name__ == "__main__":
    run()
