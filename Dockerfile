FROM python:3.11-slim

WORKDIR /app

# Copy all project files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Node.js and npm
RUN apt-get update && apt-get install -y nodejs npm && apt-get clean

# Build React frontend if dist doesn't exist
RUN if [ ! -d "documind-frontend/dist" ]; then \
    cd documind-frontend && \
    npm install && \
    npm run build && \
    cd ..; \
  fi

# Expose port
EXPOSE 8000

# Start the application
CMD ["python", "index.py"]