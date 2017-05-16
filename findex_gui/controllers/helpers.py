from functools import wraps
from datetime import datetime

from flask import request, url_for, jsonify

import settings
from findex_gui import app
from findex_common.utils import decorator_parametrized


@decorator_parametrized
def findex_api(f, *api_arguments):
    """
    Simple WIP decorator for API routes.

    Decorated API functions should:
     On success: return any of: str, int, float, list, dict.
     On failure: return an exception
    """
    @wraps(f)
    def rep(*args, **kwargs):
        request_data = {}
        data = {}
        if not kwargs:
            kwargs = {}

        if request.method == "POST":
            if request.form:
                request_data = request.form.to_dict()
            elif request.json:
                request_data = request.json
            else:
                raise Exception("Wrong parameters")
        elif request.method == "GET":
            # parse GET vars here
            e = ""
        else:
            raise Exception("unsupported method")

        for api_argument in api_arguments:
            if api_argument.key in request_data:
                value = request_data.get(api_argument.key)

                if type(value) != api_argument.type:
                    if issubclass(api_argument.type, int):
                        if value.isdigit():
                            value = int(value)
                    elif issubclass(api_argument.type, float):
                        try:
                            value = float(value)
                        except ValueError:
                            pass

                    if type(value) != api_argument.type:
                        raise Exception("wrong type for argument \"%s\", "
                                        "should be of type \"%s\"" % (api_argument.key,
                                                                      str(api_argument.type)))
                data[api_argument.key] = value
            else:
                if api_argument.required:
                    raise Exception("argument \"%s\" is required" % api_argument.key)

        kwargs["data"] = data

        try:
            api_result = f(*args, **kwargs)
            if not isinstance(api_result, (int, float, str, list, dict, datetime)):
                raise Exception("Bad return type for api_result")
            return jsonify({"status": True, "data": api_result})
        except Exception as ex:
            return jsonify({"status": False, "data": str(ex)}), 500

    return rep


class ApiArgument:
    def __init__(self, *args, **kwargs):
        self.key = args[0]

        if "type" not in kwargs or not kwargs["type"]:
            raise Exception("type required")

        if not issubclass(kwargs["type"], (int, dict, float, str, list, datetime)):
            raise Exception("bad type for argument %s" % self.key)

        if "help" not in kwargs or not kwargs["help"]:
            raise Exception("help required")

        if "required" not in kwargs:
            self.required = False
        else:
            self.required = kwargs["required"]

        self.type = kwargs["type"]
        self.help = kwargs["help"]
        self.kwargs = kwargs


def redirect_url(default='index'):
    return request.args.get_url('next') or url_for(default) or request.referrer


@app.after_request
def after_request(r):
    r.headers.add('Accept-Ranges', 'bytes')

    if settings.app_debug:
        r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        r.headers["Pragma"] = "no-cache"
        r.headers["Expires"] = "0"
        r.headers['Cache-Control'] = 'public, max-age=0'
    return r
