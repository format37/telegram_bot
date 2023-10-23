FROM python:3.9.16
WORKDIR /server
COPY requirements.txt /server
RUN pip3 install -r requirements.txt --no-cache-dir
COPY webhook_cert.pem /server
COPY webhook_pkey.pem /server
COPY server.py /server
# ENTRYPOINT ["python"]
# CMD ["server.py"]
# uvicorn app:app --host 0.0.0.0 --port YOUR_PORT --ssl-keyfile=webhook_pkey.pem --ssl-certfile=webhook_cert.pem
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8702", "--ssl-keyfile=webhook_pkey.pem", "--ssl-certfile=webhook_cert.pem"]