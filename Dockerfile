FROM python:3.10-slim

WORKDIR /bot
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app .

CMD ["python", "__main__.py"]