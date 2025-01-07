from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message":"Helloo, Liza Kapopara!"}


@app.get("/")
def get_posts():
    return {"data":"This is your post"}

@app.post("/createposts")
def create_posts():
    return{"message":"successfully created post"}