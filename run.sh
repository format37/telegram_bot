sudo docker run \
    -d \
    --restart always \
    --name telegram_bot \
    --rm \
    --network="host" \
    -v $(pwd)/bots.json:/server/bots.json \
    -v $(pwd)/config.json:/server/config.json \
    telegram_bot
