from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()
#Can I push this?

@app.get("/")
async def root():
    return {"message": "Hello World"}


app.mount("/", StaticFiles(directory="static", html=True), name="static")
