FROM python:3.14-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -i https://mirror-pypi.runflare.com/simple --trusted-host mirror-pypi.runflare.com -r requirements.txt

COPY . .