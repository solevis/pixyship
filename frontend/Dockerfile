FROM node:15-alpine

# set working directory
WORKDIR /app

# install dependencies
COPY package*.json ./
RUN npm install
RUN npm install -g @vue/cli

# copy files
COPY . /app

# serve app
EXPOSE 8080
CMD npm run serve
