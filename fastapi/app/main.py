from dataclasses import Field
from typing import Optional
from fastapi.openapi.utils import status_code_ranges
from fastapi.params import Body
from google.protobuf.descriptor import Descriptor
from pydantic import BaseModel,Field
from random import randrange

from streamlit import title

from fastapi import FastAPI, Response, status, HTTPException
# from werkzeug.exceptions import HTTPException
import psycopg2
from psycopg2.extras import RealDictCursor
import time

app = FastAPI(docs_url="/liza")

class liza(BaseModel):
    title : Optional[str] = Field(None)
    content : Optional[str]  = Field(None,description= "asdfkasdfasdfasdfasd")
    published : Optional[bool] = Field(None)

try:
    conn = psycopg2.connect(host= 'localhost', database='fastapi', user='postgres', password='postgres', cursor_factory=RealDictCursor)
    cursor = conn.cursor()
    print("Database connection was successful")

except Exception as error:
    print("Connecting the database failed")
    print("Error:", error)
    time.sleep(2)


my_posts = [{"title": "title of post 1", "content": "content of post 1", "id": 25},{"title": "favourite foods", "content": "I like pizza", "id": 26}]

@app.get("/")
def root():
    return {"message":"Helloo, Liza Kapopara!"}


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
    cursor.execute("""SELECT * FROM posts """)
    posts = cursor.fetchall()
    print(posts)
    return {"data":posts}

@app.post("/createposts")
def create_posts(payload: dict = Body(...)):
    print(payload)
    return{"new_post":f"title {payload['title']} content: {payload['content']}"}

@app.post("/gettingposts")
def getting_posts(new_post: liza):
    print(new_post)
    print(new_post.dict())
    return {"data": new_post}

@app.post("/posts3", status_code=status.HTTP_201_CREATED)
def create_posts(post: liza):
    cursor.execute(""" insert into posts (title, content, published) values (%s, %s, %s) returning *""", (post.title, post.content, post.published))
    new_post = cursor.fetchone()
    conn.commit()
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
def get_post(id: str):
    cursor.execute(""" select * from posts where id = %s""", (str(id)))
    post = cursor.fetchone()
    if not post:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                             detail = f"post with id: {id} was not found")
        # response.status_code = status.HTTP_404_NOT_FOUND
        # return {"message": f"post with id: {id} was not found"}
    return {"post_detail": post}

@app.delete("/posts/{id}", status_code=status.HTTP_200_OK)
def delete_post(id: int):

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

@app.delete("/xyz/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_posts(id: int):

    cursor.execute(""" delete from posts where id = %s returning * """, (str(id)))
    deleted_post = cursor.fetchone()
    conn.commit()

    if deleted_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} is not exists")

    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put(f"/posts/{id}")
def update_post(id: int,post: liza):
    index = find_index_post(id)

    if index == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} is not exists")

    post_dict = post.dict()
    post_dict['id'] = id
    my_posts[index] = post_dict
    return {"data": post_dict}

    # print(post)
    # return {'message': "updated post"}

@app.put("/xyz/post/{id}")
def update_post(id: int, post: liza):
    content = post.content
    title = post.title
    print(title,content)

    cursor.execute(
        f"""UPDATE posts SET
            content = CASE WHEN %s IS NOT NULL THEN %s ELSE content END,
            title = CASE WHEN %s IS NOT NULL THEN %s ELSE title END,
            published = CASE WHEN %s IS NOT NULL THEN %s ELSE published END where id = %s""",(post.content, post.content, post.title, post.title, post.published, post.published, id))
    conn.commit()

    # if not update_post:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} is not exists")

    return {"updated_data": "sfg"}


