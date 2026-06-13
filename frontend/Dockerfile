# TrendWear Frontend — nginx statik server + backendga proxy
FROM nginx:alpine

# Standart kontentni o'chirish
RUN rm -rf /usr/share/nginx/html/*

# Frontend fayllari (HTML/CSS/JS)
COPY html/ /usr/share/nginx/html/

# Nginx sozlamasi
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
