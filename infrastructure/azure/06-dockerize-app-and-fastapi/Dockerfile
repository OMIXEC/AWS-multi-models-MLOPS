FROM python:3.11-slim-bookworm

WORKDIR /app

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy app files from the fastapi local dev directory
COPY ../04-local-app-development/fastapi/ .

RUN pip install --no-cache-dir -r requirements.txt

# Azure credentials are passed as environment variables (no file mount needed)
# AZURE_STORAGE_CONNECTION_STRING is injected via docker-compose.yml

RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/')"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]
