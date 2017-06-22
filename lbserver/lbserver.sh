#!/bin/sh
# Install some packages
sudo apt-get -y update
sudo apt-get install -y python-dev
sudo apt-get install -y python-pip

#Install Erlang (the RabbitMQ runtime)--download and add Erlang to APT repository
sudo wget http://packages.erlang-solutions.com/erlang-solutions_1.0_all.deb
sudo dpkg -i erlang-solutions_1.0_all.deb
sudo apt-get update

#Install Erlang
sudo apt-get -y install socat erlang-nox

#Download the official RabbitMQ 3.6.9 .deb installer package (check the official installation guide for more: http://www.rabbitmq.com/install-debian.html)
sudo wget http://www.rabbitmq.com/releases/rabbitmq-server/v3.6.9/rabbitmq-server_3.6.9-1_all.deb

#Install the package using dpkg
sudo dpkg -i rabbitmq-server_3.6.9-1_all.deb


# enable the RabbitMQ service
sudo update-rc.d rabbitmq-server enable


#Start  the RabbitMQ service 
sudo service rabbitmq-server start

#To stop the service use the command
# sudo service rabbitmq-server stop

# Install python pika 
sudo apt-get install -y python-pika

# create users and set privileges to enable remote connection
sudo rabbitmqctl add_user test test
sudo rabbitmqctl set_user_tags test administrator
sudo rabbitmqctl set_permissions -p / test ".*" ".*" ".*"

#The nginx installation instruction is from https://cs.nginx.com/repo_setup
#Create the /etc/ssl/nginx/ directory
sudo mkdir -p /etc/ssl/nginx
# Copy two files nginx-repo.key and nginx-repo.crt to the Ubuntu Linux server into /etc/ssl/nginx/ directory
# These two files are 30 days trial version licenses, which is for the demo only. 

#Download and add the NGINX signing key
sudo wget http://nginx.org/keys/nginx_signing.key && sudo apt-key add nginx_signing.key

#Install apt utils
sudo apt-get install apt-transport-https lsb-release ca-certificates

#Add NGINX Plus repository
printf "deb https://plus-pkgs.nginx.com/ubuntu `lsb_release -cs` nginx-plus\n" | sudo tee /etc/apt/sources.list.d/nginx-plus.list

#Download the apt configuration to /etc/apt/apt.conf.d:
sudo wget -P /etc/apt/apt.conf.d https://cs.nginx.com/static/files/90nginx

#Update the repository and install NGINX Plus
sudo apt-get update
sudo apt-get install nginx-plus

#Check the nginx binary version to ensure that you have NGINX Plus installed correctly
nginx -v

#Start nginx server
sudo /usr/sbin/nginx

#Reload the conf file
sudo nginx -s reload


