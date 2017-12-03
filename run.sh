#!/bin/bash
FRONTEND=0
BACKEND=0

#function to display commands
exe() { echo "\$ ${@/eval/}" ; "$@" ; }

control_c() {
    if [[ $FRONTEND -gt 0 && $BACKEND -gt 0 ]]; then
        exe kill $BACKEND
        exe kill $FRONTEND
    else
        echo "Nothing to kill"
    fi
}

trap control_c SIGINT

if [ -d "venv" ]; then
    # Here if $DIRECTORY exists
    echo "Virtualenv venv already exists"
else
    exe virtualenv venv
fi

exe source venv/bin/activate
exe pip install -r backend/requirements.txt

exe cd frontend
exe npm install

ng serve --proxy proxy.json &
FRONTEND=$!
exe cd ../backend
python __main__.py &
BACKEND=$!

echo "Everything is running, go to http://localhost:4200"

wait $BACKEND
wait $FRONTEND
