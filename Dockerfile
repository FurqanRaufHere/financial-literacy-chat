FROM python:3.11-slim

# Set the working directory INSIDE the container
# All subsequent commands run from here
WORKDIR /app

COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# NOW copy the rest of the code
COPY . .

# Tell Docker that the container will listen on port 8000
# This is documentation — it doesn't actually open the port
EXPOSE 8000

# NEW (Gunicorn managing 3 Uvicorn workers):
CMD ["gunicorn", "src.api:app", "--workers", "3", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]