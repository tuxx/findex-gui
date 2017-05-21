class Resources {
    constructor(){

    }

    static resource_add(data){
        return FindexGui.api("/resource/add", "POST", data);
    }

    static resource_get(user_id){
        let data = {};
        if(user_id){
            data.user_id = user_id
        }

        return FindexGui.api("/resource/get", "POST", {
            "user_id": user_id
        });
    }
}