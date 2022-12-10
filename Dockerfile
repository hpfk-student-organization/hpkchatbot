FROM python:3.10-alpine
RUN apk add make automake gcc g++ subversion python3-dev --no-cache
WORKDIR /bot
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app .

RUN ls -la
RUN cd /bot/app
CMD ["python", "__main__.py"]