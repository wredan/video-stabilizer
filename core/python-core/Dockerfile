# Dockerfile.python
FROM python:3.10

# ffmpeg and libx264-dev installation
RUN apt-get update && \
    apt-get install -y ffmpeg libx264-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt && \
    pip install 'uvicorn[standard]'

COPY . /app

RUN mkdir -p data/files/input && \
    mkdir -p data/files/output

CMD python main.py
