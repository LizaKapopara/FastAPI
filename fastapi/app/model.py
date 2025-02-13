from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class User(BaseModel):
    name: str
    email: str
    otp: int

class UserUpdate(BaseModel):
    username: Optional[str] = ""
    fname: Optional[str] = ""
    lname: Optional[str]= ""
    email: Optional[str]= ""
    password: Optional[str]= ""
    mobile_no_countrycode: Optional[str]= ""
    mobile_no: Optional[int] = 0
    state: Optional[str] = ""
    city: Optional[str] = ""
    pincode: Optional[int] = 0
    is_delete: Optional[bool] = False
    is_active: Optional[bool] = False
    is_block: Optional[bool] = False
    ondate: Optional[datetime] = None

class register_user(BaseModel):
    username: str
    fname: str
    lname: str
    email: str
    password: str
    mobile_no_countrycode: str
    mobile_no: int
    state: str
    city: str
    pincode: int
    is_delete: Optional[bool] = False
    is_active: Optional[bool] = False
    is_block: Optional[bool] = False
    ondate: Optional[datetime] = None

class verify_user(BaseModel):
    email: str
    verification_link: str

class send_login_otp(BaseModel):
    username: str
    password: str

class otp_verification(BaseModel):
    email: str
    username: str
    otp: int

class Token(BaseModel):
    access_token: str
    token_type: str

class get_user(BaseModel):
    email: str

class updatepassword(BaseModel):
    email: str
    old_password: str
    new_password: str

class forget_password(BaseModel):
    email: str

class reset_password(BaseModel):
    email: str
    otp: str
    new_password: str
