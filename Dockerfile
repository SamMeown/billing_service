FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9-slim

COPY ./requirements.txt ./

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app /app/app
WORKDIR /app

EXPOSE 80
CMD ["gunicorn", "--bind ", "0.0.0.0:80", "-k", "uvicorn.workers.UvicornWorker", "app.main:app"]