FROM nginx:alpine
WORKDIR /usr/share/nginx/html

# Remove default content
RUN rm -rf ./*

# Copy only static frontend files (JS/CSS/assets)
COPY backend/app/static/ ./static/

# Copy nginx config
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
