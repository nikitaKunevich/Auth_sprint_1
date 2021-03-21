from fastapi import FastAPI

app = FastAPI()


@app.get('/hello-world')
async def hello():
    return 'Hello world!'
