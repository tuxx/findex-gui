class FindexGui {
    static api(url, method, data) {
        let _data = {
            url: `/api/v2/${url}`,
            type: method,
            contentType: 'application/json',
            timeout: 1500
        };

        if (method == "POST") {
            _data.data = data;
        }

        return $.ajax(_data).then(function(data){
            return data;
        });
        // $.ajax(_data).done(callback);
        // $.ajax(_data).fail(function(err){
        //     console.log("API exception");
        //     console.log("\turl: " + url);
        //     if(err.hasOwnProperty("message")){
        //         console.log("\terr: " + err["message"]);
        //     }
        // })
    };
}