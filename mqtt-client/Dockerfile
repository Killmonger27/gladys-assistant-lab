FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .


RUN pip install --no-cache-dir -r requirements.txt


COPY mqtt_client.py .


RUN chmod +x mqtt_client.py


CMD ["python", "mqtt_client.py"]