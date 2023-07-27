#!/bin/bash
SECONDS=0

cd $HOME/pcg-server

msg () {
    echo -e "$1\n--------------------\n"
}

msg "Stopping app"
sudo pkill pcg-server

msg "Pulling from GitHub"
git pull

msg "Entering python virtualenv"
. .venv/bin/activate

msg "Installing dependencies"
pip install -r requirements.txt

msg "Starting server in the background"
gunicorn -w 2 "app:app" --daemon

duration=$SECONDS

echo
msg "Deploy finished in $(($duration % 60)) seconds"
msg "Press Enter to exit"
read