FROM python:3.7-alpine
RUN apk add gcc build-base linux-headers
RUN mkdir /app
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD python run.py

# build: 
#  docker build -t pixyship/pixyship-backend .
# test: 
#  docker run -it -p 5000:5000 --rm --name pixyship-backend-1 pixyship/pixyship-backend
