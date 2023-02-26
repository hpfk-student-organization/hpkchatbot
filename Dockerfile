FROM python:3.10-slim

WORKDIR /app/

COPY requirements.txt requirements.txt
RUN pip install --upgrade pip  && \
    pip install -r requirements.txt && \
    pip cache purge

COPY script/docker-entrypoint.sh .
COPY app .

RUN chmod +x /app/docker-entrypoint.sh
ENTRYPOINT ["/app/docker-entrypoint.sh"]
