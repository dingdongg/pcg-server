#!/bin/bash
SECONDS=0

cd $HOME/dev/pcg-server

msg () {
    echo -e "$1\n--------------------\n"
}

msg "Stopping app"
sudo kill -HUP `ps -C gunicorn fch -o pid | head -n 1`

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
deactivate
read