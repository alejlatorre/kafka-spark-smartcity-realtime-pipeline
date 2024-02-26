FROM bitnami/spark:latest

USER root

# Install utilities
RUN apt-get update && \
    apt-get -y install curl python3-pip git vim && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# # Install Python packages
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt
