#!/bin/sh

git pull
./scripts/install-octopi.sh
make menuconfig
make clean
make

./flash.sh

