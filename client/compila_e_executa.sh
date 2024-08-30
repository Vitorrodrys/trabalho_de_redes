#!/bin/bash
if ! python3 --version | grep -q "3.11"; then
    echo "the client requires Python version 3.11"
    exit 1
fi

pip install -r requirements.txt

echo "type the server address:"
read SERVER_ADDRESS
echo "type the server port:"
read PORT

SERVER_IP=$SERVER_ADDRESS SERVER_PORT=$PORT python3 main.py
