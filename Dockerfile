FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/

RUN sed -i 's/langchain-core==0.1.31/langchain-core>=0.1.42/' requirements.txt && \
    sed -i 's/langchain_community==0.0.21/langchain-community>=0.0.32/' requirements.txt && \
    pip install --no-cache-dir -r requirements.txt

RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    pydantic \
    python-dotenv \
    langchain \
    langchain-core \
    langchain-openai

COPY . /app/

EXPOSE 8000

CMD ["python", "server.py"]