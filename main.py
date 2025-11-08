from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello FastAPI from Hackathon!"}

@app.get("/hello/{name}")
def read_item(name: str):
    return {"message": f"Hi {name}, welcome to our FastAPI app!"}
