FROM python:3.11-slim
WORKDIR /app

# Upgrade pip and install the robot runtime dependencies
RUN python -m pip install --upgrade pip setuptools wheel \
	&& pip install --no-cache-dir requests==2.31.0 websocket-client==1.9.0

COPY client.py ./client.py

# Default endpoints point to the compose services
ENV API_BASE=http://api:80
ENV WS_URL=ws://realtime:8765

CMD ["python", "client.py"]
