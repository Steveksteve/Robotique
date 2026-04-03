FROM python:3.11-slim
WORKDIR /app

# Upgrade pip and pin requests to a recent known-good version to reduce vulnerabilities
RUN python -m pip install --upgrade pip setuptools wheel \
	&& pip install --no-cache-dir requests==2.31.0

COPY client.py ./client.py

# Default API_BASE points to the api service defined in docker-compose
ENV API_BASE=http://api:80

CMD ["python", "client.py"]
