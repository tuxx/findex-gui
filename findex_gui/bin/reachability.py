import requests
from ftplib import FTP


class TestReachability:
    @staticmethod
    def test(address: str, port: int, protocol: int, user: str = None, pwd: str = None, auth_type=None):
        protocols = {
            0: TestReachability.ftp
        }
        return protocols[protocol](address, port, user, pwd)

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
