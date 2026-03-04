import warnings
warnings.filterwarnings('ignore')

import os
import time
import socket
import torch
from transformers import pipeline
from transformers import AutoImageProcessor

from scripts.data_model import NLPDataInput, NLPDataOutput, ImageDataInput, ImageDataOutput
from scripts import s3

from fastapi import FastAPI, Request, HTTPException

app = FastAPI()

device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')

####### Deploy Folder: Strictly Cloud (S3 Download Only) ##########

force_download = False 

def check_and_download_model(model_name: str):
    local_path = os.path.join('ml-models', model_name.rstrip('/'))
    # In a containerized environment, we always check if models are present
    if not os.path.isdir(local_path) or not os.listdir(local_path) or force_download:
        print(f"Downloading {model_name} from S3 into {local_path}...")
        s3.download_dir(local_path, model_name)
    return local_path

print("Initializing Production Server via S3...")

path_sentiment = check_and_download_model('tinybert-sentiment-analysis/')
sentiment_model = pipeline('text-classification', model=path_sentiment, device=device)

path_disaster = check_and_download_model('tinybert-disaster-tweet/')
tweeter_model = pipeline('text-classification', model=path_disaster, device=device)

path_pose = check_and_download_model('vit-human-pose-classification/')
image_processor = AutoImageProcessor.from_pretrained(path_pose, use_fast=True, local_files_only=True)
pose_model = pipeline('image-classification', model=path_pose, device=device, image_processor=image_processor)

######## Download ENDS  #############

@app.get("/")
def read_root():
    return {"health":"200", "hostname": socket.gethostname()}

@app.post("/api/v1/sentiment_analysis", response_model=NLPDataOutput)
def sentiment_analysis(data: NLPDataInput):
    try:
        start = time.time()
        output = sentiment_model(data.text)
        end = time.time()
        prediction_time = int((end-start)*1000)

        labels = [x['label'] for x in output]
        scores = [x['score'] for x in output]

        return NLPDataOutput(
            model_name="tinybert-sentiment-analysis",
            text=data.text,
            labels=labels,
            scores=scores,
            prediction_time=prediction_time
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/disaster_classifier", response_model=NLPDataOutput)
def disaster_classifier(data: NLPDataInput):
    try:
        start = time.time()
        output = tweeter_model(data.text)
        end = time.time()
        prediction_time = int((end-start)*1000)

        labels = [x['label'] for x in output]
        scores = [x['score'] for x in output]

        return NLPDataOutput(
            model_name="tinybert-disaster-tweet",
            text=data.text,
            labels=labels,
            scores=scores,
            prediction_time=prediction_time
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/pose_classifier", response_model=ImageDataOutput)
def pose_classifier(data: ImageDataInput):
    try:
        start = time.time()
        urls = [str(x) for x in data.url]
        output = pose_model(urls)
        end = time.time()
        prediction_time = int((end-start)*1000)

        labels = [x[0]['label'] for x in output]
        scores = [x[0]['score'] for x in output]

        return ImageDataOutput(
            model_name="vit-human-pose-classification",
            url=data.url,
            labels=labels,
            scores=scores,
            prediction_time=prediction_time
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
