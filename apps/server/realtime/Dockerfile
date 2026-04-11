FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ws_server.py ./

EXPOSE 8765

CMD ["python", "ws_server.py"]
