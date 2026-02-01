FROM python:3.11-slim

WORKDIR /app

COPY lab/requirements.txt /app/lab/requirements.txt
RUN pip install --no-cache-dir -r /app/lab/requirements.txt

COPY aegiot /app/aegiot
COPY scripts /app/scripts
COPY lab /app/lab
COPY sample_devices.csv /app/sample_devices.csv
COPY docs /app/docs

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

CMD ["python", "/app/lab/app.py"]