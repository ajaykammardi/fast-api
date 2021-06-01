FROM python:3.7-slim

WORKDIR /app

COPY ./docker/data_loader/requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

COPY ./src/data_loader/ ./src/data_loader/
COPY ./tests/data_loader/ ./tests/data_loader/
COPY ./data/ ./data/
CMD ["python", "./src/data_loader/hello.py"]