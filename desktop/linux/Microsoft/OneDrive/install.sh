#!/bin/bash

cd ~/Downloads

wget http://downloads.dlang.org/releases/2.x/2.093.1/dmd_2.093.1-0_amd64.deb

sudo dpkg -i dmd_2.093.1-0_amd64.deb

git clone https://github.com/abraunegg/onedrive.git

cd onedrive
./configure
make
sudo make install
