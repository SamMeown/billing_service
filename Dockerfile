FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9-slim

WORKDIR /usr/src/app

RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app app
COPY ./db db
COPY ./static static

EXPOSE 80
CMD ["python", "app/main.py"]