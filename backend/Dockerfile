FROM python:3.7-alpine AS build-stage

# install image dependencies
RUN apk add gcc build-base linux-headers

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# set working directory
WORKDIR /app

# install dependencies
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# copy files
COPY . .

FROM build-stage AS development-stage

# set working directory
WORKDIR /app

# copy files
COPY --from=build-stage /app .

ENV FLASK_ENV=development

# serve app
EXPOSE 5000
CMD python run.py

FROM build-stage AS production-stage

# install gunicorn wsgi server
RUN pip install gunicorn[gevent]

# set working directory
WORKDIR /app

# copy files
COPY --from=build-stage /app .

ENV FLASK_ENV=production

# serve app
EXPOSE 5000
CMD gunicorn --worker-class gevent --workers 8 --bind 0.0.0.0:5000 run:app --max-requests 10000 --timeout 5 --keep-alive 5 --log-level info