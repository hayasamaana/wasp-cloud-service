#!/bin/sh

# Install some packages
sudo apt-get -y update
sudo apt-get install -y python-dev
sudo apt-get install -y python-pip

# install python Flask web framework
sudo pip install Flask

# prepare install directory for application
mkdir /var/www
cd /var/www

#echo "Cloning repo .."
git clone https://github.com/chrinels/wasp-cloud-service.git cloud_service

export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8

# run code HERE!
cd cloud_service/rest_api
python3 server.py