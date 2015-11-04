from bottle import auth_basic, request, HTTPError


def basic_auth():
    def check(user, password):
        if user == 'admin' and password == 'admin':
            return True

    def err():
        err = HTTPError(401, "Access denied")
        err.add_header('WWW-Authenticate', 'Basic realm="%s"' % "admin area")
        return err

    user, password = request.auth or (None, None)
    if user is None or not check(user, password):
        return err()