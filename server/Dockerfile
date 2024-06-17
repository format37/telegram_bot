FROM python:3.9.16
WORKDIR /server
COPY requirements.txt /server
RUN pip3 install -r requirements.txt --no-cache-dir

# Set the timezone. Asia Tbilisi
ENV TZ=Asia/Tbilisi
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Define the count of instances as a variable
ENV INSTANCES=1

COPY server.py /server

# Cloud server:
# COPY webhook_cert.pem /cert/webhook_cert.pem
# COPY webhook_pkey.pem /cert/webhook_pkey.pem
# CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8443", "--log-level", "info", "--ssl-keyfile=/cert/webhook_pkey.pem", "--ssl-certfile=/cert/webhook_cert.pem"]

# Local server:
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "info"]
