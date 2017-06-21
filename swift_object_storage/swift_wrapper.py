from swiftclient.service import SwiftService, SwiftError, SwiftUploadObject
from swiftclient.utils import generate_temp_url
from ConfigParser import SafeConfigParser
import sys


class SwiftWrapper:
    DEFAULT_VIDEO_CONTAINER = 'vid'

    def __init__(self):
        swift_auth = self.read_conf()
        self.swift = SwiftService(swift_auth)


    def read_conf(self):
        parser = SafeConfigParser()
        try:
            parser.read('../scripts/config.properties')
        except IOError:
            print('Can not find credentials file')
            sys.exit()

        username=parser.get("auth","username")
        password=parser.get("auth","password")
        project_name=parser.get("auth","project_name")
        project_domain=parser.get("auth","project_domain_name")
        auth_url=parser.get("auth","auth_url")

        swift_auth = {"username":username,
                            "password":password,
                            "project_name":project_name,
                            "project_domain_name":project_domain,
                            "auth_url":auth_url}

        return swift_auth


if __name__ == '__main__':
    SwiftWrapper()
