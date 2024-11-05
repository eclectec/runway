from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

app = FastAPI()

origins = [
        "http://localhost",
        "http://localhost:3000"
        "http://localhost:3001"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.mount("/fils", StaticFiles(directory="/code/files"), name="files")

@app.get("/")
def test():
    return {"Hi": "There"}