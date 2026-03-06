from pydantic import BaseModel, HttpUrl


class NLPDataInput(BaseModel):
    text: list[str]
    user_id: str


class ImageDataInput(BaseModel):
    url: list[HttpUrl]
    user_id: str


class NLPDataOutput(BaseModel):
    model_name: str
    text: list[str]
    labels: list[str]
    scores: list[float]
    prediction_time: int


class ImageDataOutput(BaseModel):
    model_name: str
    url: list[HttpUrl]
    labels: list[str]
    scores: list[float]
    prediction_time: int
