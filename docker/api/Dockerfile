FROM python:3.7

RUN pip install fastapi uvicorn pytest requests

EXPOSE 8000

CMD ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000"]