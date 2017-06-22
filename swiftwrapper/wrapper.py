#! /usr/bin/env pyhon3

import sys
from os import environ
from swiftclient.service import SwiftService, SwiftError, SwiftUploadObject
from swiftclient.client import ClientException
from swiftclient.utils import generate_temp_url


class ServiceDefaults:
    DEFAULT_VIDEO_CONTAINER = 'vid'
    DEFAULT_SUCC_CONTAINER = 'transcoded'
    DEFAULT_JOB_CONTAINER = 'jobs'


class SwiftWrapper:

    def __init__(self):
        swift_auth = self.read_conf()
        try:
            self.swift = SwiftService(swift_auth)
        except ClientException as e:
            print(e)


    def read_conf(self):
        # https://docs.openstack.org/developer/python-swiftclient/service-api.html
        swift_auth = {
            "auth_version": environ.get('ST_AUTH_VERSION'),  # Should be '3'
            "os_username": environ.get('OS_USERNAME'),
            "os_password": environ.get('OS_PASSWORD'),
            "os_project_name": environ.get('OS_PROJECT_NAME'),
            "os_project_domain_name": environ.get('OS_PROJECT_DOMAIN_NAME'),
            "os_auth_url": environ.get('OS_AUTH_URL')
            }

        return swift_auth


    def list_container(self, container=ServiceDefaults.DEFAULT_VIDEO_CONTAINER):
        container_contents = []
        try:
            list_generator = self.swift.list(container=container)
            for list_res in list_generator:
                if list_res['success']:
                    for obj in list_res['listing']:
                        container_contents.append({'title':obj['name']})
                else:
                    raise list_res['error']

        except (ClientException, SwiftError) as e:
            print('Exception in "list_container":\t{}'.format(e))
            pass

        return container_contents


    def download_item(self, item, destination_dir=None):
        item_path = None
        try:
            download_generator = self.swift.download(
                                container=ServiceDefaults.DEFAULT_VIDEO_CONTAINER,
                                objects=[item],
                                options={'out_directory':destination_dir})

            for download_res in download_generator:
                    if download_res['success']:
                        item_path = download_res['path']
                        break;
                    if download_res['error']:
                        raise download_res['error']
        except (ClientException, SwiftError) as e:
            print(e)
            pass

        return item_path


    def upload_item(self, container, swift_item, object_name=None):
        upload_success = True
        try:
            if not isinstance(swift_item, SwiftUploadObject):
                swift_item = SwiftUploadObject(source=swift_item, object_name=object_name)

            upload_generator = self.swift.upload(container=container, objects=[swift_item])
            for upload_res in upload_generator:
                if not upload_res['success']:
                    raise upload_res['error']
        except (SwiftError, OSError) as e:
            print(e)
            upload_success = False
            pass

        return upload_success


if __name__ == '__main__':
    sw = SwiftWrapper()
    print(sw.list_container())
