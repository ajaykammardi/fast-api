FROM python:3.7

WORKDIR /app/
COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

EXPOSE 8000
CMD ["touch", "src/__init__.py"]
CMD ["python3", "src/api/main.py"]