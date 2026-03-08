import streamlit as st
import requests

API_BASE = "http://localhost:5000/api/v1"

st.title("MLOps Model Dashboard — Azure")

tab_sentiment, tab_disaster, tab_pose = st.tabs([
    "Sentiment Analysis",
    "Disaster Tweet",
    "Pose Classifier",
])

# --- Sentiment Analysis ---
with tab_sentiment:
    st.header("TinyBERT Sentiment Analysis")
    text_input = st.text_area("Enter review text", placeholder="Type your review here...")
    if st.button("Analyse Sentiment"):
        if text_input.strip():
            with st.spinner("Running inference..."):
                try:
                    resp = requests.post(
                        f"{API_BASE}/sentiment_analysis",
                        json={"text": [text_input]},
                        timeout=60,
                    )
                    resp.raise_for_status()
                    st.json(resp.json())
                except requests.exceptions.ConnectionError:
                    st.error("Cannot connect to FastAPI server on port 5000. Is it running?")
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("Please enter some text first.")

# --- Disaster Tweet ---
with tab_disaster:
    st.header("TinyBERT Disaster Tweet Classifier")
    tweet_input = st.text_area("Enter tweet text", placeholder="Is this tweet about a disaster?")
    if st.button("Classify Tweet"):
        if tweet_input.strip():
            with st.spinner("Running inference..."):
                try:
                    resp = requests.post(
                        f"{API_BASE}/disaster_classifier",
                        json={"text": [tweet_input]},
                        timeout=60,
                    )
                    resp.raise_for_status()
                    st.json(resp.json())
                except requests.exceptions.ConnectionError:
                    st.error("Cannot connect to FastAPI server on port 5000. Is it running?")
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("Please enter tweet text first.")

# --- Pose Classifier ---
with tab_pose:
    st.header("Vision Transformer Pose Classifier")
    url_input = st.text_input(
        "Image URL",
        placeholder="https://example.com/image.jpg",
    )
    if st.button("Classify Pose"):
        if url_input.strip():
            with st.spinner("Running inference..."):
                try:
                    resp = requests.post(
                        f"{API_BASE}/pose_classifier",
                        json={"url": [url_input]},
                        timeout=60,
                    )
                    resp.raise_for_status()
                    result = resp.json()
                    st.image(url_input, caption="Input image", use_column_width=True)
                    st.json(result)
                except requests.exceptions.ConnectionError:
                    st.error("Cannot connect to FastAPI server on port 5000. Is it running?")
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("Please provide an image URL first.")
