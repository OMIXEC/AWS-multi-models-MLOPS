from typing import Union
import time
import os
import torch
from transformers import pipeline
from transformers import AutoImageProcessor

from fastapi import FastAPI, Request, HTTPException
from scripts.data_model import (
    NLPDataInput,
    NLPDataOutput,
    ImageDataInput,
    ImageDataOutput,
)
from scripts import s3

app = FastAPI()

device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")

####### Cloud Model Loading (S3 Only) ##########

BUCKET_NAME = "mlops-multi-models"
MODEL_PREFIX = "ml-models"
LOCAL_S3_CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ml-models")


def load_model_from_s3(model_name: str):
    local_cache_path = os.path.join(LOCAL_S3_CACHE, model_name)
    if not os.path.isdir(local_cache_path) or not any(os.scandir(local_cache_path)):
        print(f"Downloading {model_name} from S3 bucket {BUCKET_NAME}...")
        s3.download_dir(local_cache_path, model_name + "/")
    print(f"Loading {model_name} from S3 Cache: {local_cache_path}")
    return local_cache_path


path_sentiment = load_model_from_s3("tinybert-sentiment-analysis")
sentiment_model = pipeline("text-classification", model=path_sentiment, device=device)

path_disaster = load_model_from_s3("tinybert-disaster-tweet")
social_media_model = pipeline("text-classification", model=path_disaster, device=device)

path_pose = load_model_from_s3("vit-human-pose-classification")
image_processor = AutoImageProcessor.from_pretrained(
    path_pose, use_fast=True, local_files_only=True
)
pose_model = pipeline(
    "image-classification",
    model=path_pose,
    device=device,
    image_processor=image_processor,
)

######## Loading ENDS  #############


@app.get("/")
def read_root():
    return {"health": "200", "mode": "aws-s3-cloud"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


@app.get("/get_sentiment/{text}")
def get_sentiment(text: str, user_id: Union[str, None] = None):
    if not text.strip():
        raise HTTPException(status_code=400, detail="Text parameter cannot be empty.")
    return {"text": text, "sentiment": "positive", "user_id": user_id}


@app.get("/api/v1/get_sentiment/")
def get_sentiment_api_v1_empty(text: str = "", user_id: Union[str, None] = None):
    if not text.strip():
        raise HTTPException(status_code=400, detail="Text parameter cannot be empty.")
    return {"text": text, "sentiment": "positive", "user_id": user_id}


@app.get("/api/v1/get_sentiment/{text}")
def get_sentiment_api_v1(text: str, user_id: Union[str, None] = None):
    if not text.strip():
        raise HTTPException(status_code=400, detail="Text parameter cannot be empty.")
    return {"text": text, "sentiment": "positive", "user_id": user_id}


@app.get("/get_sentiment_v2/{text}/{ip}")
def get_sentiment_v2(text: str, ip: str, user_id: Union[str, None] = None):
    return {"ip": ip, "text": text, "sentiment": "positive", "user_id": user_id}


@app.post("/get_twitter_sentiment")
def get_twitter_sentiment(text: str, ip: str, user_id: Union[str, None] = None):
    return {"ip": ip, "text": text, "sentiment": "normal", "user_id": user_id}


@app.post("/get_twitter_sentiment_v2")
async def get_twitter_sentiment_v2(request: Request):
    try:
        data = await request.json()
        text: str = data.get("text")
        ip = data.get("ip")
        user_id = data.get("user_id")

        if not text or not ip:
            raise HTTPException(
                status_code=400, detail="Missing required fields: text or ip"
            )

        return {"ip": ip, "text": text, "sentiment": "normal", "user_id": user_id}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=400, detail="Invalid JSON format or bad request"
        )


@app.post("/api/v1/sentiment_analysis", response_model=NLPDataOutput)
def sentiment_analysis(data: NLPDataInput):
    try:
        if not data.text:
            raise HTTPException(
                status_code=400, detail="Input text list cannot be empty."
            )

        start = time.time()
        output = sentiment_model(data.text)
        end = time.time()
        prediction_time = int((end - start) * 1000)

        labels = [x["label"] for x in output]
        scores = [x["score"] for x in output]

        output_data = NLPDataOutput(
            model_name="tinybert-sentiment-analysis",
            text=data.text,
            labels=labels,
            scores=scores,
            prediction_time=prediction_time,
        )
        return output_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing sentiment analysis: {str(e)}"
        )


@app.post("/api/v1/disaster_classifier", response_model=NLPDataOutput)
def disaster_classifier(data: NLPDataInput):
    try:
        if not data.text:
            raise HTTPException(
                status_code=400, detail="Input text list cannot be empty."
            )

        start = time.time()
        output = social_media_model(data.text)
        end = time.time()
        prediction_time = int((end - start) * 1000)

        labels = [x["label"] for x in output]
        scores = [x["score"] for x in output]

        output_data = NLPDataOutput(
            model_name="tinybert-disaster-tweet",
            text=data.text,
            labels=labels,
            scores=scores,
            prediction_time=prediction_time,
        )
        return output_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing disaster classification: {str(e)}",
        )


@app.post("/api/v1/pose_classifier", response_model=ImageDataOutput)
def pose_classifier(data: ImageDataInput):
    try:
        if not data.url:
            raise HTTPException(
                status_code=400, detail="Input url list cannot be empty."
            )

        start = time.time()
        urls = [str(x) for x in data.url]
        output = pose_model(urls)
        end = time.time()
        prediction_time = int((end - start) * 1000)

        labels = [x[0]["label"] for x in output]
        scores = [x[0]["score"] for x in output]

        output_data = ImageDataOutput(
            model_name="vit-human-pose-classification",
            url=data.url,
            labels=labels,
            scores=scores,
            prediction_time=prediction_time,
        )
        return output_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing pose classification: {str(e)}"
        )
