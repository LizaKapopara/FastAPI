from typing import Optional
from fastapi.openapi.utils import status_code_ranges
from fastapi.params import Body
from pydantic import BaseModel
from random import randrange
from fastapi import FastAPI,Response,status
from werkzeug.exceptions import HTTPException


class liza(BaseModel):
    name : str
    age : int
    published: bool = True
    rating: Optional[int] = None

app = FastAPI()

@app.get("/")
def root():
    return {"message":"Helloo, Liza Kapopara!"}

my_posts = [{"title": "title of post 1", "content": "content of post 1", "id": 25},{"title": "favourite foods", "content": "I like pizza", "id": 26}]

def find_post(id):
    for p in my_posts:
        if p["id"] == id:
            return p

def find_index_post(id):
    for i,p in enumerate(my_posts):
        if p['id'] == id:
            return i

@app.get("/posts")
def get_posts():
    return {"data":my_posts}

@app.post("/createposts")
def create_posts(payload: dict = Body(...)):
    print(payload)
    return{"new_post":f"title {payload['title']} content: {payload['content']}"}



@app.post("/gettingposts")
def getting_posts(new_post: liza):
    print(new_post)
    print(new_post.dict())
    return {"data": new_post}

@app.post("/posts2", status_code=status.HTTP_201_CREATED)
def create_postss(post: liza):
    post_dict = post.dict()
    post_dict['id'] = randrange(0, 1000000)
    my_posts.append(post_dict)
    return {"data": post_dict}

@app.get("/posts/latest")
def get_latest_post():
    post = my_posts[len(my_posts)-1]
    return {"detail": post}

@app.get("/posts/{id}")
def get_post(id: int, response: Response):
    post = find_post(id)
    if not post:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                             detail = f"post with id: {id} was not found")
        # response.status_code = status.HTTP_404_NOT_FOUND
        # return {"message": f"post with id: {id} was not found"}
    return {"post_detail": post}


from fastapi import FastAPI, HTTPException, status

@app.delete("/posts/{id}", status_code=status.HTTP_200_OK)
def delete_post(id: int):
    # Find the index of the post to delete
    index = find_index_post(id)

        # Raise HTTPException with a 404 error and a detailed message

    if id == 25:
        return {"message": f"Post with id {id} was successfully deleted"}
    if id == 26:
        return {"message": f"Post with id {id} was successfully deleted"}

    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id: {id} was not found"
        )