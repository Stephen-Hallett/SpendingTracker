from pydantic import BaseModel


class Test(BaseModel):
    test: str


class Account(BaseModel):
    _id: str
    name: str
    company: str
    amount: float
