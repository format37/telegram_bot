FROM python:3.9.16
WORKDIR /server
COPY requirements.txt /server
RUN pip3 install -r requirements.txt --no-cache-dir
# COPY webhook_cert.pem /server
# COPY webhook_pkey.pem /server
COPY server.py /server
# CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8443", "--ssl-keyfile=webhook_pkey.pem", "--ssl-certfile=webhook_cert.pem"]
# CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8443", "--ssl-keyfile=/cert/webhook_cert.pem", "--ssl-certfile=/cert/webhook_pkey.pem"]
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8443", "--log-level", "warning", "--ssl-keyfile=/cert/webhook_pkey.pem", "--ssl-certfile=/cert/webhook_cert.pem"]
CMD ["gunicorn", "-w", "2", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--timeout", "120", "server:app", "--log-level", "warning", "--ssl-keyfile=/cert/webhook_pkey.pem", "--ssl-certfile=/cert/webhook_cert.pem"]