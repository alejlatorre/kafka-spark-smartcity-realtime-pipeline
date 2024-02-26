FROM bitnami/spark:latest

USER root

# Install utilities
RUN apt-get update && \
    apt-get -y install curl python3-pip git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# # Install Python packages
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

# Copy .env file
COPY .env /opt/bitnami/spark/.env

# Copy Spark jobs folder
COPY ./jobs /opt/bitnami/spark/jobs

# Expose ports
EXPOSE 8080 7077