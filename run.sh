sudo docker stop telegram_bot
sudo docker rm telegram_bot
sudo docker run \
    -d \
    --restart always \
    --name telegram_bot \
    --network="host" \
    -v $(pwd)/bots.json:/server/bots.json \
    -v $(pwd)/config.json:/server/config.json \
    telegram_bot
