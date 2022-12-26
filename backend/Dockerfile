FROM python:3.10.7-slim-buster AS python-for-flask

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY poetry.lock pyproject.toml /app/
RUN pip3 install poetry

COPY . /app/

RUN poetry install

COPY  ./scripts/entrypoint.sh ./scripts/start.sh ./scripts/start.prod.sh  /

RUN sed -i 's/\r$//g' /start.sh && chmod +x /start.sh && sed -i 's/\r$//g' /start.prod.sh && chmod +x /start.prod.sh && sed -i 's/\r$//g' /entrypoint.sh && chmod +x /entrypoint.sh 