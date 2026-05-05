FROM python:3.11-slim

WORKDIR /app/paper-scraper

COPY paper-scraper/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY paper-scraper/ .

CMD ["/bin/sh", "-c", "uvicorn src.api.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
