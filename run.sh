# sudo docker run -d --restart always -p 7401:7401  partners_bot --name partners_bot
sudo docker run \
    --name telegram_bot \
    --rm \
    --network="host" \
    -v $(pwd)/bots.json:/server/bots.json \
    -v $(pwd)/config.json:/server/config.json
    telegram_bot
# sudo docker run -p 7401:7401  partners_bot
