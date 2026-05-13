FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install DREXPA from GitHub
RUN pip install --no-cache-dir git+https://github.com/druglogics/drexpa.git

# Copy app files
COPY drexpa/ ./drexpa/
COPY .streamlit/ ./.streamlit/

# Expose Streamlit port
EXPOSE 8501

# Configure Streamlit
RUN mkdir -p ~/.streamlit && \
    echo "[server]" > ~/.streamlit/config.toml && \
    echo "headless = true" >> ~/.streamlit/config.toml && \
    echo "port = 8501" >> ~/.streamlit/config.toml && \
    echo "enableCORS = false" >> ~/.streamlit/config.toml

# Run Streamlit
CMD ["streamlit", "run", "drexpa/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
