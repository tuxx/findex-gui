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

class FancyTable {
    /**
     * dynatable.js helper function that initializes a table using ajax.
     * @param {string} api - remote json api
     * @param {string} target - jQuery object
     * @param {function} func_rowWriter - function responsible for drawing html rows
     * @param {function} func_drawErrorMsg - function responsible for drawing error messages
     */
    static init(api, target, func_rowWriter, func_drawErrorMsg, search_disabled){
        if(func_drawErrorMsg) {
            target.bind('dynatable:ajax:error', function (e, dynatable) {
                func_drawErrorMsg("Could not fetch rows.");
            });
        }

        let data = {
            dataset: {
                ajax: true,
                ajaxUrl: api,
                ajaxOnLoad: true,
                records: []
            },
            table: {
                defaultColumnIdStyle: 'underscore'
            },
            features: {
                paginate: true,
                sort: false,
                pushState: false,
                search: true,
                recordCount: true,
                perPageSelect: true
            }
        };

        if(search_disabled){
            data.features.search = false;
        }

        if(func_rowWriter){
            if(!data.hasOwnProperty("writers")){
                data["writers"] = {};
            }
            data["writers"]["_rowWriter"] = func_rowWriter;
        }
        return target.dynatable(data);
    }
}
