#!/bin/sh

# set hostname
sudo echo waspmq-backend > /etc/hostname
sudo sed -i "s/127.0.0.1 localhost/127.0.0.1 waspmq-backend/g" /etc/hosts

# install some dependencies
sudo apt-get -y update
sudo apt-get install -y python-dev
sudo apt-get install -y python-pip
sudo apt-get install -y python-pika
sudo apt-get install -y mencoder

# prepare directory
mkdir /usr/local/
cd /usr/local/


# Clone the git repo
cd /home/ubuntu


git clone https://github.com/chrinels/wasp-cloud-service.git
cd wasp-cloud-service
