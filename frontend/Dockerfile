FROM node:16-alpine AS base-stage
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .

FROM node:16-alpine AS build-stage
WORKDIR /app
COPY --from=base-stage /app /app
RUN npm run build

FROM nginx:alpine
COPY --from=build-stage /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
