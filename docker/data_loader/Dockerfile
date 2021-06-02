FROM python:3.7

WORKDIR /app/
COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

CMD ["python3","src/data_loader/main.py"]