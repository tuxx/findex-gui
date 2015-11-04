import requests

# # curl -X POST http://127.0.0.1:7080 -d '{"params": [], "method": "status"}'


class JsonRpcClient():
    def __init__(self):
        self.req = requests.session()
        self.headers = {
            'User-Agent': 'Mozilla 4.3'
        }

    def post(self, url, method, params):
        try:
            return self.req.post(
                url=url,
                headers=self.headers,
                data={
                    "params": params,
                    "method": method
                }
            ).content
        except Exception as ex:
            e = ''

    # def test(self):
    #     x = self.post("http://192.168.XXX.XXX:7080", "status", [])
    #     print x


class Resourcer():
    def __init__(self, db, findex):
        self.db = db
        self.findex = findex


    def get_resources(self):
        resources = self.findex.get_resource_objects()
