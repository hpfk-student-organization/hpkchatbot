FROM python:3.10-slim

WORKDIR /bot
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app .

CMD ["python", "main.py"]