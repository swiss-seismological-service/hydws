# Dockerizing HYDWS
# Following the instructions from:
#
# https://gitlab.seismo.ethz.ch/armdanie/hydws
#
# Build Container:
# docker build -t hydws:1.0 .
#
# Run Container:
# docker run [-d] [--rm] [--name hydws] -p 8080:80 hydws:1.0
#
# Modify running container:
# docker exec -it hydws /bin/bash

# Base image
FROM phusion/baseimage:latest

# Add label metadata
LABEL maintainer="Daniel Armbruster"
LABEL email="daniel.armbruster@sed.ethz.ch"

CMD ["/sbin/my_init"]

# Install Python 3.6
RUN add-apt-repository ppa:deadsnakes/ppa

# System dependencies
RUN apt-get update && apt-get install -y git \
                                         python3.6 \
                                         python3-pip \
                                         pkg-config \
                                         build-essential \
                                         libssl-dev \
                                         libffi-dev \
                                         libpython3.6-dev \
                                         apache2 \
                                         apache2-dev

# Update pip
RUN python3.6 -m pip install --upgrade pip

# Install mod_wsgi
RUN python3.6 -m pip install mod_wsgi
RUN mod_wsgi-express module-config | head -n 1 > \
  /etc/apache2/mods-available/wsgi.load
RUN mod_wsgi-express module-config | tail -n 1 > \
  /etc/apache2/mods-available/wsgi.conf
RUN a2enmod wsgi

# Get the source from GitLab:master
RUN git clone https://gitlab.seismo.ethz.ch/armdanie/hydws.git /var/www/hydws

# Install the services
WORKDIR /var/www/hydws
RUN python3.6 -m pip install .[postgres]

# Copy Apache configuration configuration
COPY hydws.conf /etc/apache2/sites-available/

# Copy the WSGI configuration scripts
COPY *.wsgi /var/www/hydws/apache2/

# The default configuration
COPY hydws_config /var/www/hydws/config/

# Give read permissions
RUN chmod +r /var/www/hydws/config/hydws_config /var/www/hydws/apache2/*.wsgi

# Disable the Apache2 default configuration
RUN a2dissite 000-default
# Enable the supplied WSGI modules
RUN a2ensite hydws.conf

# Add the apache2 service
RUN mkdir /etc/service/apache2 && \
	echo "#!/bin/sh\nexec apachectl -D FOREGROUND" > /etc/service/apache2/run && \
	chmod +x /etc/service/apache2/run

RUN mkdir -p /var/www/hydws/log && chown www-data:www-data /var/www/hydws/log

# Add the logging configuration
COPY logging.conf /var/www/hydws/config/logging.conf

# Expose Apache2 default port
EXPOSE 80

# Clean up (baseimage recommended)
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
