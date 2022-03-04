#!/bin/bash
# check if docker image exists
result=$( docker images -q test-manager )
if [ -z "$result" ]
then
    docker build --tag test-manager .
fi
docker run -d -p 5000:5000 test-manager
echo "App running on port 5000"
