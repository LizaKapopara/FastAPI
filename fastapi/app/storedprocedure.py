import hashlib
import random
import re
import secrets
import smtplib
import string
from datetime import timedelta, datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import psycopg2
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError,jwt
from pandas import notna
from psycopg.generators import fetch
from psycopg2.extras import RealDictCursor

from fastapi import FastAPI, HTTPException, Depends
from . import model
from .model import reset_password

# from model import User
# from app import model

# from app.model import UserUpdate


secret_key = "hihereliza"
algorithm = "HS256"

app = FastAPI(docs_url="/liza")

try:
    conn = psycopg2.connect(host= 'localhost', database='jointask', user='postgres', password='postgres', cursor_factory=RealDictCursor)
    # cursor = conn.cursor()
    print("Database connection was successful")

except Exception as error:
    print("Connecting the database failed")
    print("Error:", error)
#     time.sleep(2)

get_otp =''.join(random.choices(string.digits,k=6))

# @app.post("/users/", response_model=dict)
# def create_user(user: model.User):
#     name_regex = "^[A-Za-z ]+$"
#     if not re.match(name_regex, user.name):
#         raise HTTPException(status_code=400,
#                             detail="Invalid name")
#
#     EMAIL_REGEX = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
#     if not re.match(EMAIL_REGEX, user.email):
#         raise HTTPException(status_code=400,
#                             detail="invalid email", )
#     try:
#         cursor.execute("SELECT 1 FROM users WHERE email = %s;", (user.email,))
#         if cursor.fetchone():
#             raise HTTPException(status_code=400, detail=f"{user.email} Email already exists create another one!")
#
#         cursor.execute("CALL create_user(%s :: varchar(50), %s :: varchar(100), %s :: int);", (user.name, user.email, get_otp))
#         conn.commit()
#         return {"your otp is": get_otp}
#
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))

# @app.post("/verifyuser/", response_model = dict)
# def verify_user(user: model.User):
#     try:
#         cursor.execute("CALL verify_user(%s :: varchar(50), %s :: varchar(100), %s :: int, %s :: varchar(50))", (user.name, user.email, user.otp, ))
#         result = cursor.fetchall()
#         conn.commit()
#         cursor.close()
#         print(result)
#         return{"message": "success"}
#
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))





@app.get("/getusers/{user_id}")
def get_user_by_id():

    cursor.execute(f"CALL getuserbydepartment('liz'); fetch all {'liz'}")
    # cursor.execute(f"CALL getuserid({user_id}, 'liz'); fetch all {'liz'}")

    user = cursor.fetchall()

    print(user)
    conn.commit()
    cursor.close()
    if user:
        return user
    raise HTTPException(status_code=404, detail="User not found")


@app.delete("/deleteusers/{user_id}", response_model=dict)
def delete_user(user_id: int):
    cursor.execute("CALL delete_user(%s :: int);", (user_id,))

    conn.commit()
    cursor.close()
    return  {"message": "User deleted successfully"}

def generate_token(email: str) -> str:
    """Generate a unique verification token."""
    random_token = secrets.token_hex(16)
    return hashlib.sha256((email + random_token).encode()).hexdigest()

@app.post("/user/", response_model=dict)
def create_users(user: model.register_user):
    cursor = conn.cursor()
    username_regex = "^[A-Za-z][A-Za-z0-9_]{7,29}$"
    if not re.match(username_regex, user.username):
        raise HTTPException(status_code=400,
                            detail="Invalid username, your username should contain only alphanumeric character and underscore and it should be minimum of length 7!")

    fname_regex = "[a-zA-Z '-]{1,25}"
    if not re.match(fname_regex, user.fname):
        raise HTTPException(status_code=400,
                            detail="Invalid fname, your username should contain only alphabets and hyphen and apostrophe and should maximum of 24 character and minimum of 1 character!")

    lname_regex = "[a-zA-Z '-]{1,25}"
    if not re.match(lname_regex, user.lname):
        raise HTTPException(status_code=400,
                            detail="Invalid lname, your username should contain only alphabets and hyphen and apostrophe and should maximum of 24 character and minimum of 1 character!")

    EMAIL_REGEX = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    if not re.match(EMAIL_REGEX, user.email):
        raise HTTPException(status_code=400,
                            detail="invalid email")

    password_regex = "^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$"
    if not re.match(password_regex, user.password):
        raise HTTPException(status_code=400,
                            detail="password should contain atleast one uppercase character,one lowercase character,0-9 number and one special character!")

    countrycode_regex = "^\+([1-9]{1}[0-9]{0,3})$"
    if not re.match(countrycode_regex, user.mobile_no_countrycode):
        raise HTTPException(status_code=400,
                            detail="country code invalid")

    verification_expiry = datetime.now() + timedelta(minutes=10)
    print(verification_expiry)
    verification_token = generate_token(user.email)
    verification_link = f"http://localhost:8000/verify-email?token={verification_token}"

    print("verification_token============", verification_token)

    try:
        cursor.execute("SELECT 1 FROM user_registration WHERE username = %s;", (user.username,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail=f"{user.username} already exists create another one!")

        cursor.execute("SELECT 1 FROM user_registration WHERE email = %s;", (user.email,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail=f"{user.email} Email already exists create another one!")


        mobile_no = int(user.mobile_no)
        cursor.execute("SELECT 1 FROM user_registration WHERE mobile_no = %s;", (mobile_no,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail=f"{user.mobile_no} already exists create another one!")

        # cursor.execute("CALL user_registration (%s :: varchar(100), %s :: varchar(100), %s :: varchar(100), %s :: varchar(100), %s :: varchar(100), %s :: text, %s :: bigint, %s :: varchar(100), %s :: varchar(100), %s :: numeric, %s :: bool, %s :: bool, %s :: bool, %s :: timestamp, %s, %s);",
                       # (user.username, user.fname, user.lname, user.email, user.password, user.mobile_no_countrycode, user.mobile_no, user.state, user.city, user.pincode, user.is_delete, user.is_active, user.is_block, user.ondate, verification_expiry, verification_token))
        # conn.commit()

        cursor.execute(f"CALL user_registration(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);",
                       (user.username, user.fname, user.lname, user.email, user.password, user.mobile_no_countrycode,
                        user.mobile_no, user.state, user.city, user.pincode, user.is_delete, user.is_active,
                        user.is_block, verification_expiry, verification_link, 'result'))

        cursor.execute("FETCH ALL from result;")
        print("======")
        print("======", user.username, user.fname, user.lname, user.email, user.password, user.mobile_no_countrycode,
                        user.mobile_no, user.state, user.city, user.pincode, user.is_delete, user.is_active,
                        user.is_block, verification_expiry, verification_link, 'result')
        print("======")
        sasa = cursor.fetchall()
        print("result", sasa)
        conn.commit()
        cursor.close()

        send_verification_email(user.email, user.username, verification_token)

        return {"message": sasa}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    # finally:
    #     cursor.close()
    #     conn.commit()

def send_verification_email(to_email: str, username: str, token: str):

    verification_link = f"http://localhost:8000/verify-email?token={token}"

    msg = MIMEMultipart()
    msg['From'] = "lizakapopara8@gmail.com"
    msg['To'] = to_email
    msg['Subject'] = "Please verify your email"

    # Email body
    # Email setup
    body = f"Hello,\n\nPlease verify your email by clicking the link below:\n\n{verification_link}"
    msg.attach(MIMEText(body, 'plain'))

    # Send email via SMTP
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login("lizakapopara8@gmail.com", "lxlx zusu hdoe teik")
        text = msg.as_string()
        server.sendmail("lizakapopara8@gmail.com", to_email, text)



@app.post("/verify-email/")
def verify_email(user: model.verify_user):
    cursor = conn.cursor()
    try:
        cursor.execute("Select email,verification_link from user_registration WHERE email = %s and is_active = false", (user.email, ))
        fetch = cursor.fetchone()
        print(fetch)

        if fetch is None:
            raise HTTPException(status_code=400,detail = "User already Verified..........")

        if(fetch['email'] == user.email and fetch['verification_link'] == user.verification_link):


            cursor.execute("SELECT verification_expiry FROM user_registration WHERE email = %s and verification_link = %s", (user.email,user.verification_link,))
            usedddr = cursor.fetchone()
            print(usedddr)


            if not usedddr:
                raise HTTPException(status_code=400, detail="Invalid or expired verification link.")

            # verification_expiry = user
            verification_expiry = usedddr['verification_expiry']
            current_time = datetime.now()

            if verification_expiry < current_time:
                raise HTTPException(status_code=400, detail="Verification link has expired. Please register again.")

            cursor.execute("UPDATE user_registration SET is_active = TRUE WHERE email = %s", (user.email,))
            conn.commit()
            cursor.close()




        else:
            raise HTTPException(status_code=400, detail="you have already verified or your credentials not matched!")
        return {"message": "Your email has been successfully verified. You can now log in."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # finally:
    #     cursor.close()
    #     conn.commit()



@app.post("/loginuser/")
def send_login_otp(user: model.send_login_otp):
    cursor = conn.cursor()
    try:
        cursor.execute(f"CALL user_login_request(%s, %s, %s);",(user.username, user.password, 'getresult'))
        cursor.execute("FETCH ALL from getresult;")
        result = cursor.fetchall()
        print(result)
        # cursor.close()
        # cursor.execute(f" Close {getresult};")
        conn.commit()
        cursor.close()

        if not result:
            raise HTTPException(status_code=400, detail="username or password invalid")

        user_info = result[0]
        print(user_info)
        email = user_info["email"]
        otp = user_info["login_otp"]

        print(otp)


        send_otp_email(email, otp)

        return {"message": "check you email for verification otp!"}


    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    # finally:
    #     cursor.close()
    #     conn.commit()


def send_otp_email(to_email,login_otp):

    msg = MIMEMultipart()
    msg['From'] = "lizakapopara8@gmail.com"
    msg['To'] = to_email
    msg['Subject'] = "Please verify your email"

    # Email body
    # Email setup
    body = f"Hello,\n\nHere is your login_otp\n\n{login_otp}"
    msg.attach(MIMEText(body, 'plain'))

    # Send email via SMTP
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login("lizakapopara8@gmail.com", "lxlx zusu hdoe teik")
        text = msg.as_string()
        server.sendmail("lizakapopara8@gmail.com", to_email, text)


oauth = OAuth2PasswordBearer(tokenUrl="login")


@app.post("/verifyotp/")
def verify_otp(data: model.otp_verification):
    cursor = conn.cursor()
    cursor.execute("CALL verify_user_otp (%s, %s, 'result');", (data.username, data.otp))
    cursor.execute("FETCH ALL FROM result;")
    result = cursor.fetchall()
    conn.commit()
    cursor.close()
    print("result------------------------", result)
    if result is not None:
        if result[0]['msgcode'] == 'true':
            token = create_access_token({"email": data.email})
            return {"access_token": token, "token_type": "bearer", "email": data.email}
        else:
            raise HTTPException(status_code=400, detail=result[0]['msg'])
    else:
        raise HTTPException(status_code=400, detail='Data Not Found')



    # finally:
    #     cursor.close()
    #     conn.commit()


def create_access_token(data: dict):
    to_encode =  data.copy()
    expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm = algorithm)

    return  encoded_jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        email: str = payload.get("email")
        if email is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication credentials",
            )
        return email  # Return username from token
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


@app.get("/user/details/")
def get_user_details(email: model.get_user, current_user: str = Depends(get_current_user)):
    cursor = conn.cursor()
    print(email)
    print(current_user)
    if email.email != current_user:
        raise HTTPException(status_code=403, detail="Access denied")


    cursor.execute("SELECT * FROM user_registration WHERE email = %s;", (email.email,))
    demo = cursor.fetchone()
    conn.commit()
    cursor.close()
    if not demo:
        raise HTTPException(status_code=404, detail="User not found")

    return {"Details": demo}




@app.post("/update_latest_password/")
def update_latest_password(pwd: model.updatepassword, current_user: str = Depends(get_current_user)):
    cursor = conn.cursor()
    try:
        if pwd.email == current_user:
            if pwd.old_password == pwd.new_password:
                raise HTTPException(status_code=401,
                                    detail = "your new password cannot be as your old password")

            cursor.execute(f"CALL update_password (%s, %s, %s, %s);", (pwd.email, pwd.old_password, pwd.new_password, 'result'))
            cursor.execute("FETCH ALL from result;")
            sasa = cursor.fetchall()
            conn.commit()
            cursor.close()

            return {"message": sasa}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/updateusers/", response_model=dict)
def update_user(user: model.UserUpdate, current_user: str = Depends(get_current_user)):
    cursor = conn.cursor()
    try:
        print("------------------", user.lname)
        print(user.email)
        print(current_user)
        if user.email != current_user:
            raise HTTPException(status_code=403, detail="Unauthorized to update this user as you have to enter email throw which you created your account!")

        cursor.execute("CALL update_user(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);", (user.username, user.fname, user.lname, user.email, user.password, user.mobile_no_countrycode, user.mobile_no, user.state, user.city, user.pincode, user.is_delete, user.is_active, user.is_block, 'result'))
        cursor.execute("fetch all from result")
        response = cursor.fetchall()
        print(response)
        conn.commit()
        cursor.close()

        if not response:
            raise HTTPException(status_code=404, detail="No data returned from update")


        return {"message": response}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/forgot_password/")
def forgot_password(data: model.forget_password):
    cursor = conn.cursor()
    try:
        # otp = str(random.randint(100000, 999999))
        otp = ''.join(random.choices(string.digits, k=6))

        cursor.execute(
            """
            UPDATE user_registration 
            SET login_otp = %s, otp_created_at = NOW()
            WHERE email = %s;
            """,
            (otp, data.email),
        )
        conn.commit()
        cursor.close()

        send_otp_email(data.email, otp)

        return {"message": "Password reset OTP sent successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/reset_password/")
def reset_password(data: model.reset_password):
    cursor = conn.cursor()
    try:
        jsonobject = { "password":"data.new_password"}
        cursor.execute("CALL reset_password(%s, %s, %s, 'result');", (data.email, data.otp, data.new_password))
        cursor.execute("FETCH ALL FROM result;")
        result = cursor.fetchall()
        conn.commit()
        cursor.close()
        return {"message": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/dynamicqueryupadte/")
def dynamicqueryupadte(data: model.reset_password):
    cursor = conn.cursor()
    try:
        jsonobject = { "password":f"{data.new_password}", }
        cursor.execute("CALL update_user_details(%L, %s);", (18, jsonobject))
        cursor.execute("FETCH ALL FROM result;")
        result = cursor.fetchall()
        conn.commit()
        cursor.close()
        return {"message": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
