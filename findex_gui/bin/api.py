from functools import wraps
from datetime import datetime, date

from flask import request, url_for, jsonify
from flask.json import JSONEncoder

from findex_gui.bin.utils import get_request_data
from findex_common.utils import decorator_parametrized


class ApiJsonEncoder(JSONEncoder):
    '''Custom JSON encoder for flask.jsonify that returns ISO 8601
    strings which can be parsed in javascript with Date.parse()'''
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return super().default(obj)


@decorator_parametrized
def FindexApi(f, *api_arguments):

    """A simple decorator for API routes.
    Validates incoming request parameters. The method can be any
    of: GET, POST, PATCH, DELETE.
    The view function itself may return any of the following data types:
    str, int, float, list, dict. On failure, an exception can be
    raised within the view function itself, which in turn yields
    JSON stating the error.
    Basic example:
        app.route('/api/user/login', methods=['POST'])
        @api(
            Parameter('username', type=str, required=True, help='Username'),
            Parameter('password', type=str, required=True, help='Password')
        )
        def api_user_login(data):
            username = data.get('username')
            password = data.get('password')
            return 'username: %s, password: %s' % (username, password)
    """
    @wraps(f)
    def _params(*args, **kwargs):
        if not kwargs:
            kwargs = {}
        request_data = get_request_data()

        data = {}
        for api_argument in api_arguments:
            if api_argument.key not in request_data:
                if api_argument.required:
                    raise Exception('argument \'%s\' is required' % api_argument.key)
                else:
                    continue

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
                    raise Exception('wrong type for argument \'%s\', '
                                    'should be of type \'%s\'' % (api_argument.key,
                                                                  str(api_argument.type)))
            data[api_argument.key] = value
        kwargs['data'] = data

        try:
            api_result = f(*args, **kwargs)
            if api_result is None:
                return jsonify({'status': True, 'data': None})
            elif not isinstance(api_result, (int, float, str, list, dict, datetime)):
                raise Exception('Bad return type for api_result')
            return jsonify({'status': True, 'data': api_result})
        except Exception as ex:
            return jsonify({'status': False, 'data': str(ex)}), 500
    return _params


class api_arg:
    def __init__(self, *args, **kwargs):
        self.key = args[0]

        if 'type' not in kwargs or not kwargs['type']:
            raise Exception('type required')

        if not issubclass(kwargs['type'], (int, dict, float, str, list, datetime)):
            raise Exception('bad type for argument %s' % self.key)

        if 'help' not in kwargs or not kwargs['help']:
            raise Exception('help required')

        if 'required' not in kwargs:
            self.required = False
        else:
            self.required = kwargs['required']

        self.type = kwargs['type']
        self.help = kwargs['help']
        self.kwargs = kwargs


