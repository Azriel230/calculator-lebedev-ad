if [[ -z $(docker images -a | grep "server") ]]; then
  docker build -t nekoch4n/calculator-server .
fi

if [[ -z $(docker ps -a | grep "server") ]]; then
  docker run --network host --name server -d nekoch4n/calculator-server
else
  docker start server
fi
