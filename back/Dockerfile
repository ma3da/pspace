FROM python:3.8.6-buster

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt

CMD ["uwsgi", "app.ini"]
