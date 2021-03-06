from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from task_routes import router as task_router
from category_routes import router as category_router
from plotting import router as plots_router

app = FastAPI()
app.include_router(task_router)
app.include_router(category_router)
app.include_router(plots_router)


app.mount("/", StaticFiles(directory="static", html=True), name="static")



@app.route("/hello")
def hello():
    return {"message": "Hello World"}