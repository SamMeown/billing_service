from fastapi import FastAPI

app = FastAPI()


@app.get('/')
def index():
    return dict(message="Hello world")
