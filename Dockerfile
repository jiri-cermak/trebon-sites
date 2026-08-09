# Single container serving all three domains.
# Based on V5 Design Specification Section 0.5.
FROM nginx:alpine
COPY penzion/ thai/ masaze/ /usr/share/nginx/html/
COPY css/ /usr/share/nginx/html/css/
COPY js/ /usr/share/nginx/html/js/
COPY img/ /usr/share/nginx/html/img/
COPY fonts/ /usr/share/nginx/html/fonts/
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY shared.conf /etc/nginx/conf.d/shared.conf
