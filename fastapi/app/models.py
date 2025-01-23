import re
from sqlalchemy import Column, String, Boolean, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import validates
from .database import Base


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    published = Column(Boolean, server_default='TRUE', nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('now()'))
    email = Column(String, unique=True, nullable=False)
    # owner_id = Column(Integer, ForeignKey(
    #     "users.id", ondelete="CASCADE"), nullable=False)

    # owner = relationship("User")

    @validates("email")
    def validate_email(self, key, value):
            # Validate email using regular expression (e.g., standard email format)
        email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
        if not re.match(email_regex, value):
            raise ValueError("Invalid email format.")
        return value

