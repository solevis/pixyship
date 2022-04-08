FROM python:3.7-alpine
RUN apk add gcc build-base linux-headers
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
ENTRYPOINT [ "python" ]
CMD ["run.py" ]

# build: 
#  docker build -t pixyship/pixyship-backend .
# test: 
#  docker run -it -p 5000:5000 --rm --name pixyship-backend-1 pixyship/pixyship-backend
