FROM node:22-alpine as base-stage
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .

FROM node:22-alpine as build-stage
WORKDIR /app
COPY --from=base-stage /app /app
RUN npm run build

FROM nginx:stable-alpine as production-stage
COPY --from=build-stage /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
