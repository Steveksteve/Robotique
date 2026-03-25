FROM php:8.1-apache

ENV APACHE_DOCUMENT_ROOT /var/www/html/public

# Reduce layer size, update packages and install  required packages
RUN set -eux; \
    apt-get update; \
    apt-get upgrade -y; \
    apt-get install -y --no-install-recommends libzip-dev unzip curl; \
    docker-php-ext-install pdo pdo_mysql; \
    a2enmod rewrite; \
    apt-get clean; \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*;

# Configure DocumentRoot to /var/www/html/public
RUN sed -ri 's!DocumentRoot /var/www/html!DocumentRoot ${APACHE_DOCUMENT_ROOT}!g' /etc/apache2/sites-available/*.conf \
    && sed -ri 's!<Directory /var/www/html>!<Directory ${APACHE_DOCUMENT_ROOT}>!g' /etc/apache2/apache2.conf

COPY . /var/www/html

WORKDIR /var/www/html/public

RUN chown -R www-data:www-data /var/www/html

EXPOSE 80

CMD ["apache2-foreground"]
