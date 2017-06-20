`pip install python-openstackclient && pip install python-swiftclient`

openstack container create CONTAINER_NAME
openstack container show CONTAINER_NAME

swift upload FILE CONTAINER_NAME
swift list
swift list CONTAINER_NAME

openstack container show CONTAINER_NAME

swift stat -v
