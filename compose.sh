# # Create folder ./id_garden if not exists
# if [ ! -d "./id_garden" ]; then
#   mkdir ./id_garden
# fi
# # Remove all files in id_garden
# rm -rf ./id_garden/*

# Cloud server
# rm -rf ./server/webhook_cert.pem
# rm -rf ./server/webhook_pkey.pem
# sudo cp /etc/letsencrypt/live/service.icecorp.ru-0001/fullchain.pem ./server/webhook_cert.pem
# sudo cp /etc/letsencrypt/live/service.icecorp.ru-0001/privkey.pem ./server/webhook_pkey.pem
# sudo chmod -R 777 ./server/webhook_cert.pem
# sudo chmod -R 777 ./server/webhook_pkey.pem

# Down and up docker-compose
sudo docker compose down -v
sudo docker compose up --build --force-recreate --remove-orphans -d