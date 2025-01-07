from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message":"Helloo, Liza Kapopara!"}


@app.get("/post")
def get_posts():
    return {"data":"This is your post"}