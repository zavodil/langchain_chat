FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir \
    langchain==0.1.16 \
    langchain-core==0.1.52 \
    langchain-community==0.0.38 \
    langchain-openai==0.1.7 \
    pydantic>=2.5.2 \
    fastapi>=0.104.1 \
    uvicorn>=0.24.0 \
    python-dotenv>=1.0.0 \
    openai>=1.3.0 \
    requests>=2.31.0 \
    aiohttp>=3.9.1 \
    httpx>=0.25.2 \
    orjson>=3.9.10 \
    typing_extensions>=4.8.0

COPY . .

RUN if [ -f app.py ]; then echo "app.py found"; else echo "Creating placeholder app.py"; echo "# Placeholder for app module" > app.py; fi

RUN if [ -f tools.json ]; then echo "tools.json found"; else echo "Creating empty tools.json"; echo "[]" > tools.json; fi

RUN if [ -f input.json ]; then echo "input.json found"; else echo "Creating empty input.json"; echo "{}" > input.json; fi

EXPOSE 8000

CMD ["python", "server.py"]