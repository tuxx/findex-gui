import requests
from ftplib import FTP


class TestReachability:
    @staticmethod
    def test(server_address: str, resource_port: int, resource_protocol: int,
             auth_user: str = None, auth_pass: str = None, auth_type=None):
        protocols = {
            0: TestReachability.ftp
        }
        return protocols[resource_protocol](server_address, resource_port, auth_user, auth_pass)

    @staticmethod
    def ftp(address, port, user=None, pwd=None, auth_type=None):
        ftp = FTP()
        try:
            ftp.connect(address, port)
            if user and pwd:
                ftp.login(user, pwd)
            else:
                ftp.login("anonymous", "anonymous")
            ftp.retrlines("LIST")
            return True
        except:
            return False
