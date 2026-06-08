# syntax=docker/dockerfile:1

# Use the official Python Alpine image as base
FROM python:alpine AS build

# Description of resulting image
LABEL org.opencontainers.image.description="Web application template"

# Set the working directory within the container
ARG workdir='/opt/webapp'
WORKDIR "${workdir}"

# Update pip and install Python dependencies
ENV PIP_ROOT_USER_ACTION=ignore
COPY ./requirements.txt /abrechnungsformular/requirements.txt
RUN pip3 install --upgrade pip && pip3 install --no-cache-dir --upgrade -r /abrechnungsformular/requirements.txt

# Copy the Python app into the container
COPY app/ "${workdir}/app/"
COPY main.py "${workdir}/"
COPY templates/ "${workdir}/templates/"
COPY static/ "${workdir}/static/"
COPY --chmod=+x tools/generate_config.py "${workdir}/tools/"
COPY tools/templates/ "${workdir}/tools/templates/"

# Setup non-root user to run the app (security best practice)
ARG UID=10001
RUN adduser --disabled-password --gecos "" --home "/nonexistent" --shell "/sbin/nologin" --no-create-home --uid "${UID}" appuser
USER appuser

# Expose a port for the web application
EXPOSE 8000

# Define the command to run the Flask application using Gunicorn
CMD ["gunicorn", "--bind=0.0.0.0:8000", "--workers=2", "--no-control-socket", "main:flaskapp"]
