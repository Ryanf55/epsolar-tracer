#!/bin/bash

scp ~/Development/epsolar-tracer/pyepsolartracer/client.py pi@10.0.0.33:/home/pi/Development/epsolar-tracer/pyepsolartracer/
scp ~/Development/epsolar-tracer/$1 pi@10.0.0.33:/home/pi/Development/epsolar-tracer/


echo python3 /home/pi/Development/epsolar-tracer/$1


ssh pi@10.0.0.33 python3 /home/pi/Development/epsolar-tracer/$1
