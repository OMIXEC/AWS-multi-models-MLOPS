# ML Model Serving over REST API

## What is a REST API?
A REST (Representational State Transfer) API is an architectural style for an application program interface (API) that uses HTTP requests to access and use data.

In the context of Model Serving:
1. **Model Training:** Produces a model object.
2. **Prediction:** The model is wrapped in an API.
3. **Application/Client:** Sends data to the API and receives predictions back.

**Common Tools used for Python API Serving:**
* FastAPI
* Flask
* TensorFlow Serving
* Nginx, Uvicorn, Gunicorn (for server orchestration)

## API Request Types
* **GET:** Retrieve data.
* **POST:** Submit new data.
* **PUT:** Update existing data.
* **DELETE:** Remove data.

*Flow:* A REST client sends a REST request (GET/POST/PUT/DELETE) to a REST server. The server processes the resource and sends back a REST response (typically in JSON or XML format).

## API Response Types
Responses typically come in JSON format and include status codes.
Example components:
* `id`, `main`, `description`
* `temp`, `pressure`, `humidity`
* Status codes (200 OK, 404 Not Found, 500 Server Error)

## What is FastAPI?
FastAPI is a modern, fast (high-performance), web framework for building APIs with Python 3.6+ based on standard Python type hints.
* **Step 1 (Build FastAPI):** Wrap the prediction model in FastAPI and run it via an ASGI server like Uvicorn. The server handles Request/Response routing.
* **Step 2 (Deploy):** The entire FastAPI application is then packaged into a Docker container for standardized deployment across any environment.
