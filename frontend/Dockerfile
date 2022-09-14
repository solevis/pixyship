FROM node:lts-alpine AS build-stage

# set working directory
WORKDIR /app

# install dependencies
COPY package*.json ./
RUN npm install
RUN npm install -g @vue/cli

# copy files
COPY . .

FROM build-stage AS development-stage

ENV NODE_ENV=development
ENV CHOKIDAR_USEPOLLING=true

# serve app
EXPOSE 8080
CMD npm run serve

FROM build-stage AS production-stage

ENV NODE_ENV=production

# generate app
RUN npm run build
