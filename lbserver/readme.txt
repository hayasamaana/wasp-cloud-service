This folder contains instructions/scripts for the load balancer.
The load balancer is the entry point seen by the end-user/client. 
It will pass the user to the webserver depending on the specified balancing algorithm. 
It can accept RPC from the operation module (running on another VM) to complete the scale up/down. 
The operation module should provide the ip address of the scaled VM and the type of desired operation(scale up/down) to the load balancer
