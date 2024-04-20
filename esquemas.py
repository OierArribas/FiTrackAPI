from pydantic import BaseModel

class User(BaseModel):
    username: str
    email: str or None = None
    hashed_password: str or None = None
    fotoBirmap: bytes or None = None

    class Config:
        orm_mode = True
