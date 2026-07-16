# syntax=docker/dockerfile:1

# Use the official Python Alpine image as base
FROM python:3.14-alpine3.24 AS build

# Description of resulting image
LABEL org.opencontainers.image.description="Ein Webserver, über den Schulen sich für eine Auszeichnung als fahrradfreundliche Schule bewerben können."

# Set the working directory within the container
ARG workdir='/opt/fahrradschule'
WORKDIR "${workdir}"

# Install required packages
RUN apk add --no-cache libmagic

# Update pip and install Python dependencies
ENV PIP_ROOT_USER_ACTION=ignore
COPY ./requirements.txt /abrechnungsformular/requirements.txt
RUN pip3 install --upgrade pip && pip3 install --no-cache-dir --upgrade -r /abrechnungsformular/requirements.txt

# Setup non-root user to run the app (security best practice)
ARG UID=10001
RUN adduser --disabled-password --gecos "" --home "/nonexistent" --shell "/sbin/nologin" --no-create-home --uid "${UID}" appuser

# Generate empty directory for configuration files
ENV FAHRRADSCHULE_CONFIG_DIR=/etc/opt/fahrradschule
RUN mkdir "$FAHRRADSCHULE_CONFIG_DIR"

# Generate empty directory for variable data
ENV FAHRRADSCHULE_SAVE_DIR=/var/opt/fahrradschule
RUN mkdir -m 777 "$FAHRRADSCHULE_SAVE_DIR"

# Copy system files into the container
COPY --chmod=0755 docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh

# Copy the Python app into the container
COPY main.py "${workdir}/"
COPY static/ "${workdir}/static/"
COPY templates/ "${workdir}/templates/"
COPY --chmod=+x tools/generate_config.py tools/initdb.py "${workdir}/tools/"
COPY tools/templates/ "${workdir}/tools/templates/"
COPY app/ "${workdir}/app/"

# Expose a port for the web application
EXPOSE 8000

# Define default settings for Flask
ENV FLASK_MAX_CONTENT_LENGTH=1048576

# Define default executable and the command to run the Flask application using Gunicorn
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD ["gunicorn", "--bind=0.0.0.0:8000", "--workers=2", "--no-control-socket", "main:flaskapp"]

# Store version number as environment variable
ARG VERSION
ENV DOCKER_IMAGE_VERSION=${VERSION}
