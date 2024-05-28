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
# CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8443", "--ssl-keyfile=webhook_pkey.pem", "--ssl-certfile=webhook_cert.pem"]
# CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8443", "--ssl-keyfile=/cert/webhook_cert.pem", "--ssl-certfile=/cert/webhook_pkey.pem"]
# CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8443", "--log-level", "warning", "--ssl-keyfile=/cert/webhook_pkey.pem", "--ssl-certfile=/cert/webhook_cert.pem"]
CMD ["gunicorn", "-w", $INSTANCES, "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8443", "--timeout", "120", "server:app", "--log-level", "warning", "--keyfile=/cert/webhook_pkey.pem", "--certfile=/cert/webhook_cert.pem"]
