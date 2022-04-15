FROM python:3.7-alpine

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

# serve app
EXPOSE 5000
CMD python run.py
