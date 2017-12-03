#!/bin/bash
FRONTEND=0
BACKEND=0
SENSORS=0
ACTUATORS=0

#function to display commands
exe() { echo "\$ ${@/eval/}" ; "$@" ; }

control_c() {
    if [[ $FRONTEND -gt 0 && $BACKEND -gt 0 && $SENSORS -gt 0 && $ACTUATORS -gt 0 ]]; then
        exe kill $BACKEND
        exe kill $FRONTEND
        exe kill $SENSORS
        exe kill $ACTUATORS
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
exe cd ../

python fake-sensors &
SENSORS=$!
sleep 2
python fake-actuators &
ACTUATORS=$!
sleep 2
exe rm db.sq3
python backend &
BACKEND=$!

wait $BACKEND
wait $FRONTEND
