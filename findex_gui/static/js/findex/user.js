class UserController extends FindexGui {
    constructor() {
        super();
    }

    static add(username, password) {
        let data = {
            "username": username,
            "password": password
        };

        return FindexGui.api("/user/register", "POST", data);
    }

    static remove(username){
        let data = {
            "username": username
        };

        return FindexGui.api("/user/delete", "POST", data);
    }
}
