FROM node:15-alpine as develop-stage
RUN mkdir /app
WORKDIR /app
COPY package*.json ./
RUN npm install -g @vue/cli
RUN npm install
COPY . .

FROM develop-stage as build-stage
RUN npm run build

FROM nginx:1.20.2-alpine as production-stage
COPY --from=build-stage /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]

# build: 
#  docker build -t pixyship/pixyship-frontend .
# test: 
#  docker run -it -p 8080:80 --rm --name pixyship-frontend-1 pixyship/pixyship-frontend
# get built dist: 
#  docker ps | grep pixyship-frontend | awk '{print $1}'
#  docker cp $(docker ps | grep pixyship-frontend | awk '{print $1}'):/usr/share/nginx/html ./dist
