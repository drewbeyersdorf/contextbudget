FROM python:3.12-slim

WORKDIR /app

# Install deps first for layer caching -- requirements change less often than code
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8091

# Single worker is fine for SQLite (no concurrent write contention).
# Scale horizontally by running multiple containers with separate DBs,
# or switch to Postgres when you outgrow single-node.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8091"]
