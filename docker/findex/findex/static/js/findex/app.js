class FindexGui {
    constructor(){

    }
    
    static api(url, method, data) {
        let _data = {
            url: `${APPLICATION_ROOT}api/v2${url}`,
            type: method,
            contentType: 'application/json',
            timeout: 15500
        };

        if (method == "POST") {
            _data.data = JSON.stringify(data);
        }

        return $.ajax(_data).then(function(data){
            return data;
        }).fail(function(data) {
            return data;
        });
    };
}
