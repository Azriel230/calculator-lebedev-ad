if [[ -z $(docker images -a | grep "server") ]]; then
  docker build -t server .
fi

if [[ -z $(docker ps -a | grep "server") ]]; then
  docker run --network host --name server -d server
else
  docker start server
fi
