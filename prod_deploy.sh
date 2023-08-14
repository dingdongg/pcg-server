#!/bin/bash
SECONDS=0

cd $HOME/dev/pcg-server

msg () {
    echo -e "$1\n--------------------\n"
}

msg "Pulling from GitHub"
git pull

msg "Stopping container..."
sudo docker stop pgs-container

msg "Removing container..."
sudo docker rm pgs-container

msg "Removing image..."
sudo docker rmi pgs

msg "Re-building image..."
sudo docker build --tag pgs .

msg "Running container..."
sudo docker run -d -p 9000:9000 --name pgs-container pgs

duration=$SECONDS

echo
msg "Deploy finished in $(($duration % 60)) seconds"
msg "Press Enter to exit"
deactivate
read