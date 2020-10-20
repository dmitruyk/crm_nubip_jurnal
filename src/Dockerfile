FROM python:3.6

ENV DEASY_GUNICORN_NUMBER_OF_WORKERS=2

RUN python -m pip install --upgrade pip

COPY requirements.txt /requirements.txt

RUN pip install -r /requirements.txt

COPY . /test

WORKDIR /test

COPY ./docker-entrypoint.sh /docker-entrypoint.sh

RUN chmod +xxx /docker-entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/docker-entrypoint.sh"]
