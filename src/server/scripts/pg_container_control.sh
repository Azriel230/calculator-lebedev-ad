if [[ -z $(docker ps -a | grep "database") ]]; then
  /bin/bash ./src/server/scripts/pg_new_container.sh
else
  docker start database
fi
