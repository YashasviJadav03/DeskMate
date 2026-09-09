FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend app and data
COPY app/ ./app/
COPY ../data/ ./data/

# Environment defaults
ENV PYTHONUNBUFFERED=1 \
    LLM_PROVIDER=mock \
    CHROMA_DB_PATH=/app/data/chroma_db \
    LOGS_DB_PATH=/app/data/logs.db \
    TICKETS_DB_PATH=/app/data/tickets.db \
    DOCS_PATH=/app/data/docs

# Ingest knowledge documents into ChromaDB
RUN python -m app.knowledge.ingest

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
