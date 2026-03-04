from typing import Union
import time
import os
import torch
from transformers import pipeline
from transformers import AutoImageProcessor

from fastapi import FastAPI, Request, HTTPException
from scripts.data_model import NLPDataInput, NLPDataOutput, ImageDataInput, ImageDataOutput

app = FastAPI()

device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')

####### Load ML Models Directly from 02-model-training ##########
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.abspath(os.path.join(BASE_DIR, '../../02-model-training'))

path_sentiment = os.path.join(MODELS_DIR, 'sentiment_classification/tinybert-sentiment-analysis')
sentiment_model = pipeline('text-classification', model=path_sentiment, device=device)

path_disaster = os.path.join(MODELS_DIR, 'disaster_tweets_classification/tinybert-disaster-tweet')
tweeter_model = pipeline('text-classification', model=path_disaster, device=device)

path_pose = os.path.join(MODELS_DIR, 'human_pose_classification/vit-human-pose-classification')
image_processor = AutoImageProcessor.from_pretrained(path_pose, use_fast=True, local_files_only=True)
pose_model = pipeline('image-classification', model=path_pose, device=device, image_processor=image_processor)

######## Loading ENDS  #############

@app.get("/")
def read_root():
    return {"health":"200"}

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
    except Exception as e:
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
        output = tweeter_model(data.text)
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