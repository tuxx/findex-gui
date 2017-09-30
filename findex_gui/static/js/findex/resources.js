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

    static nmap_cmd(hosts, ports){
        return `nmap --max-rtt-timeout 200ms -sT -PN -T5 -p${ports} -oG - ${hosts}`
    }
}
