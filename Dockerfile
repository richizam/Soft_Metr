# Dockerfile
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Expose the port (FastAPI will run on 8000 inside the container)
EXPOSE 8000

# Default command: run the FastAPI app.
# (The telegram_bot service will override this command.)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
