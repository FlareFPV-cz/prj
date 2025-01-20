from fastapi import FastAPI
from routers import analysis
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Mount the "output" directory to serve static files

app = FastAPI()

app.mount("/output", StaticFiles(directory="output"), name="output")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analysis.router)

@app.get("/")
def read_root():
    return {"message": "Drone Analysis App is running"}
