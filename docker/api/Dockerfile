FROM python:3.7

WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["python3", "-m" , "flask", "run", "--host=0.0.0.0"]