FROM node:20-alpine AS build
WORKDIR /app

COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./
ARG VITE_API_BASE=/api
ARG VITE_WS_URL=
ENV VITE_API_BASE=${VITE_API_BASE}
ENV VITE_WS_URL=${VITE_WS_URL}
RUN npm run build

FROM nginx:1.27-alpine
COPY apps/web/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
