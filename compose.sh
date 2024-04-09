# sudo docker-compose up --build --force-recreate -d --remove-orphans
# sudo docker-compose up --build -d
# echo "Compose approach is deprecated. Please, use build."
echo "to fix run: sudo docker-compose down -v"
sudo docker-compose up --build --force-recreate --remove-orphans -d
