from typing import Union
import time
import os
import torch
from transformers import pipeline
from transformers import AutoImageProcessor

from fastapi import FastAPI, Request, HTTPException
from scripts.data_model import NLPDataInput, NLPDataOutput, ImageDataInput, ImageDataOutput
from scripts import s3

app = FastAPI()

device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')

####### Model Loading Logic: Hybrid (Local Support + Cloud Fallback) ##########

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Path to the training directory
EXTERNAL_TRAINING_DIR = os.path.abspath(os.path.join(BASE_DIR, '../../02-model-training'))
# Path to local S3 cache
LOCAL_S3_CACHE = os.path.join(BASE_DIR, 'ml-models')

def get_model_path(model_subdir: str, model_name: str):
    """
    Checks for the model in the training directory first (local support).
    If not found, falls back to downloading from S3 into a local cache (cloud support).
    """
    # 1. Check external training directory (Local)
    local_training_path = os.path.join(EXTERNAL_TRAINING_DIR, model_subdir, model_name)
    if os.path.isdir(local_training_path) and any(os.scandir(local_training_path)):
        print(f"Loading {model_name} from Local Training Dir: {local_training_path}")
        return local_training_path

    # 2. Check local S3 cache or download (Cloud)
    local_cache_path = os.path.join(LOCAL_S3_CACHE, model_name)
    if not os.path.isdir(local_cache_path) or not any(os.scandir(local_cache_path)):
        print(f"Model not found locally. Downloading {model_name} from S3...")
        s3.download_dir(local_cache_path, model_name + '/')
    
    print(f"Loading {model_name} from S3 Cache: {local_cache_path}")
    return local_cache_path

# Load Sentiment Model
path_sentiment = get_model_path('sentiment_classification', 'tinybert-sentiment-analysis')
sentiment_model = pipeline('text-classification', model=path_sentiment, device=device)

# Load Disaster Model
path_disaster = get_model_path('disaster_tweets_classification', 'tinybert-disaster-tweet')
social_media_model = pipeline('text-classification', model=path_disaster, device=device)

# Load Pose Model
path_pose = get_model_path('human_pose_classification', 'vit-human-pose-classification')
image_processor = AutoImageProcessor.from_pretrained(path_pose, use_fast=True, local_files_only=True)
pose_model = pipeline('image-classification', model=path_pose, device=device, image_processor=image_processor)

######## Loading ENDS  #############

@app.get("/")
def read_root():
    return {"health":"200", "mode": "hybrid"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

# Legacy endpoints
@app.get("/get_sentiment/{text}")
def get_sentiment(text: str, user_id: Union[str, None] = None):
    if not text.strip():
        raise HTTPException(status_code=400, detail="Text parameter cannot be empty.")
    return {"text": text, "sentiment": "positive", "user_id": user_id}

# New /api/v1/ endpoints to match Postman queries
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
        text:str = data.get('text')
        ip = data.get('ip')
        user_id = data.get('user_id')

        if not text or not ip:
            raise HTTPException(status_code=400, detail="Missing required fields: text or ip")

        return {"ip": ip, "text": text, "sentiment": "normal", "user_id": user_id}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON format or bad request")

# Real ML Endpoints
@app.post("/api/v1/sentiment_analysis", response_model=NLPDataOutput)
def sentiment_analysis(data: NLPDataInput):
    try:
        if not data.text:
            raise HTTPException(status_code=400, detail="Input text list cannot be empty.")
            
        start = time.time()
        output = sentiment_model(data.text)
        end = time.time()
        prediction_time = int((end-start)*1000)

        labels = [x['label'] for x in output]
        scores = [x['score'] for x in output]

        output_data = NLPDataOutput(
            model_name="tinybert-sentiment-analysis",
            text=data.text,
            labels=labels,
            scores=scores,
            prediction_time=prediction_time
        )
        return output_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing sentiment analysis: {str(e)}")

@app.post("/api/v1/disaster_classifier", response_model=NLPDataOutput)
def disaster_classifier(data: NLPDataInput):
    try:
        if not data.text:
            raise HTTPException(status_code=400, detail="Input text list cannot be empty.")

        start = time.time()
        output = social_media_model(data.text)
        end = time.time()
        prediction_time = int((end-start)*1000)

        labels = [x['label'] for x in output]
        scores = [x['score'] for x in output]

        output_data = NLPDataOutput(
            model_name="tinybert-disaster-tweet",
            text=data.text,
            labels=labels,
            scores=scores,
            prediction_time=prediction_time
        )
        return output_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing disaster classification: {str(e)}")

@app.post("/api/v1/pose_classifier", response_model=ImageDataOutput)
def pose_classifier(data: ImageDataInput):
    try:
        if not data.url:
            raise HTTPException(status_code=400, detail="Input url list cannot be empty.")

        start = time.time()
        urls = [str(x) for x in data.url]
        output = pose_model(urls)
        end = time.time()
        prediction_time = int((end-start)*1000)

        labels = [x[0]['label'] for x in output]
        scores = [x[0]['score'] for x in output]

        output_data = ImageDataOutput(
            model_name="vit-human-pose-classification",
            url=data.url,
            labels=labels,
            scores=scores,
            prediction_time=prediction_time
        )
        return output_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing pose classification: {str(e)}")
