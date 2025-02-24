from pydantic import BaseModel, constr


class PostCreate(BaseModel):
    text: constr(max_length=1000000)


class PostOut(PostCreate):
    id: int
    user_id: int

    class Config:
        orm_mode = True
