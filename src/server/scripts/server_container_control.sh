if [[ -z $(docker images -a | grep "server") ]]; then
  docker build -t server .
fi

if [[ -z $(docker ps -a | grep "server") ]]; then
  docker run --network host server -d
else
  docker start server
fi
