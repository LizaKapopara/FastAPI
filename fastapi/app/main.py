import os
from typing import Optional, Tuple, Any
from pathlib import Path

from fastapi.encoders import jsonable_encoder
from multipart import file_path
from fastapi.responses import FileResponse

from fastapi import FastAPI, Response, status, HTTPException, Depends, File, UploadFile
from fastapi.params import Body
from pydantic import BaseModel
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from sqlalchemy.orm import Session
from app import models
from .database import engine, get_db
import re


models.Base.metadata.create_all(bind=engine)

app = FastAPI(docs_url="/liza")



class liza(BaseModel):
    title : str
    content : str
    published : bool
    email : str

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


# @app.get("/sqlalchemy")
# def test_posts(db: Session = Depends(get_db)):
#
#     posts = db.query(models.Post)
#     print(posts)
#     return{"data": "dfgu"}



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
    EMAIL_REGEX = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    if not re.match(EMAIL_REGEX, post.email):
        raise HTTPException(status_code = 400,
                             detail = "invalid email",)

    cursor.execute("""select email from posts where email = %s""", (post.email,))
    existing_email = cursor.fetchone()

    if existing_email:
        raise HTTPException(status_code=400,
                            detail="email already exists",)

    cursor.execute(""" insert into posts (title, content, published, email) values (%s, %s, %s, %s) returning *""", (post.title, post.content, post.published, post.email))
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
    cursor.execute(""" select file_name from posts where id = %s""", (str(id)))
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

# @app.delete("/xyz/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
# def delete_posts(id: str):
#
#     cursor.execute(""" delete from posts where id = %s returning * """, (id))
#     deleted_post = cursor.fetchone()
#     conn.commit()
#
#     if deleted_post == None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} is not exists")
#     return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.delete("/xyz/posts/{idd}", status_code=status.HTTP_204_NO_CONTENT)
def delete_posts(idd: str):
    ID_REGEX = r"^\d+$"

    if not re.match(ID_REGEX, idd):
        raise HTTPException(
            status_code=400,
            detail="Invalid ID. ID should only contain digits (0-9)."
        )
    print(f"select count(id) as count FROM posts WHERE id = {int(idd)}")

    cursor.execute("select count(id) as count FROM posts WHERE id = {}".format(int(idd)))
    getdata  = cursor.fetchone()
    print(getdata)
    print(len(getdata))
    if len(getdata) > 0 :
        # Continue with deletion if the ID is valid
        cursor.execute(f"DELETE FROM posts WHERE id =  {int(idd)}  RETURNING * ")
        deleted_post = cursor.fetchone()
        conn.commit()

        if not deleted_post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Post with id: {idd} does not exist"
            )

        return Response(status_code=status.HTTP_204_NO_CONTENT)

    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id: {idd} does not exist"
        )

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

    # cursor.execute(
    #     f"""UPDATE posts SET
    #                 content = CASE when COALESCE(NULLIF (%S, ''), NULL) IS NOT NULL THEN %s ELSE content END
    #
    #         content = CASE WHEN %s IS NOT NULL THEN %s ELSE content END,
    #         title = CASE WHEN %s IS NOT NULL THEN %s ELSE title END,
    #         published = CASE WHEN %s IS NOT NULL THEN %s ELSE published END where id = %s""",(post.content, post.content, post.title, post.title, post.published, post.published, id))
    cursor.execute("""
    UPDATE posts SET 
    content = CASE when COALESCE(NULLIF (%s, ''), NULL) IS NOT NULL THEN %s ELSE content END,
    title = CASE when COALESCE(NULLIF (%s, ''), NULL) IS NOT NULL THEN %s ELSE title END,
    published = CASE when %s IS NOT NULL THEN %s ELSE published END where id = %s returning *
    """,(post.content, post.content, post.title, post.title, post.published, post.published, id))
    result = cursor.fetchall()
    print(result)
    conn.commit()

    # if not update_post:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} is not exists")

    return {"updated_data": "sfg"}


@app.get("/getdataaa")
async def getdata():
    cursor = conn.cursor()
    cursor.execute("select * from posts")
    conn.commit()
    result = cursor.fetchall()

    return {"data":result}

class uploading(BaseModel):
    id : int
    email : str

@app.post("/create_file/")
async def image(image: UploadFile = File(...)):
    try:
        os.mkdir("images")
        print(os.getcwd())
    except Exception as e:
        print(e)
    file_name = os.path.join(os.getcwd(), "images", image.filename.replace(" ", "-"))
    with open(file_name,'wb+') as f:
        f.write(image.file.read())
        f.close()
    file = jsonable_encoder({"imagePath":file_name})
    return {"filename": file_name}
    conn.commit()

@app.post("/upload")
async def upload(post: liza = Depends(), files: list[UploadFile] = File()):
    EMAIL_REGEX = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    if not re.match(EMAIL_REGEX, post.email):
        raise HTTPException(status_code=400,
                            detail="invalid email", )

    cursor.execute("""select email from posts where email = %s""", (post.email,))
    existing_email = cursor.fetchone()

    if existing_email:
        raise HTTPException(status_code=400,
                            detail="email already exists", )

    try:
        upload_directory = os.path.join(os.getcwd(), "uploads")
        os.makedirs(upload_directory, exist_ok=True)

        file_paths = []
        for file in files:
            file_path = os.path.join(upload_directory, file.filename)
            contents = file.file.read()
            with open(file_path, 'wb') as f:
                f.write(contents)
            normalized_path = file_path.replace("\\", "/")
            file_paths.append(normalized_path)

    except Exception:
        raise HTTPException(status_code=500, detail='Something went wrong')
    finally:
        for file in files:
            file.file.close()

    cursor.execute(""" insert into posts (title, content, published, email, file_name) values (%s, %s, %s, %s, %s) returning *""",
               (post.title, post.content, post.published, post.email, ", ".join(file_paths)),)
    new_post = cursor.fetchone()
    return {"data": new_post}


@app.get(f"/gettingfile/{id}")
async def get_file(id: int):
    try:
        cursor.execute("""select file_name from posts where id = %s""", (id, ))
        result = cursor.fetchone()

        file_path = result['file_name']
        print("-------",file_path.split(","))
        ddd = file_path.split(",")
        for i in ddd:
            file_name = os.path.basename(i)
            with open(file_name, "w", encoding="utf-8") as output_file:
                output_file.write(i)

        return "done"
        conn.commit()
        # link = []
        # for file_path,file_name in zip(file_paths,file_names):
        #     x = FileResponse(file_path, media_type='application/octet-stream', filename=f"{file_names}")
        #     link.append(file_name,file_path)
        # print(link)

        # return FileResponse(i, media_type='application/octet-stream', filename=f"{file_name}")

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


