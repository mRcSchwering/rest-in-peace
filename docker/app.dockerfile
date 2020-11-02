FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

EXPOSE 8000

COPY . /app
WORKDIR /app

RUN pip install -r app/requirements.txt && chmod +x docker/entrypoint.sh

CMD [ "docker/entrypoint.sh" ]
