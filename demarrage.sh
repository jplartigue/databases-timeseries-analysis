#!/bin/bash

sleep 10


python manage.py migrate --database postgres
python manage.py migrate --database timescale

tail -f /dev/null