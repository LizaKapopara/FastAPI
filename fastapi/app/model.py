from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class User(BaseModel):
    name: str
    email: str
    otp: int

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None

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
    username: str
    otp: int

class Token(BaseModel):
    access_token: str
    token_type: str

class get_user(BaseModel):
    username: str

class updatepassword(BaseModel):
    email: str
    old_password: str
    new_password: str
