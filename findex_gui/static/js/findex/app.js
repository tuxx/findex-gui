class FindexGui {
    constructor(){

    }
    
    static api(url, method, data) {
        let _data = {
            url: `${APPLICATION_ROOT}api/v2${url}`,
            type: method,
            data: data,
            timeout: 15500
        };

        if (method != "GET") {
            if(typeof _data.data !== 'undefined') _data.data = JSON.stringify(data);
            _data.contentType = 'application/json'
        }

        return $.ajax(_data).then(function(data){
            return data;
        }).fail(function(data) {
            console.log("==ERROR==");
            console.log(data);
            console.log("=========");
            return data;
        });
    };

    static api_unpack_error(data){
        let val = null;
        if(typeof data === "object"){
            if(data.hasOwnProperty("data")) {
                val = data.data;
            } else if(data.hasOwnProperty("responseText")){
                try {
                    val = JSON.parse(data.responseText);
                    if(val.hasOwnProperty("data")){
                        val = val.data;
                    } else {
                        throw(":(");
                    }
                } catch (e) {
                    val = data.responseText;
                }

            } else {
                debugger;
                val = "Could not get repr for type Object";
            }
        } else {
            val = data;
        }
        return val;
    }
}
