"use strict";

class Search {
    constructor(application_root, autocomplete, per_page, selectors) {
        this.autocomplete = autocomplete;
        this.per_page = per_page;
        this.selectors = selectors;
        this.application_root = application_root;
    }

    /**
     * Calling this method will gather the filters and do a search query
     * @return
     */
    search(page){
        if (page == null){
            page = 0;
        }

        let params = this._gather_params('params');

        params['autocomplete'] = this.autocomplete;
        params['per_page'] = this.per_page;
        params['page'] = page;
        params['key'] = this.get_key();

        if(params['key'] == '') return;

        this._search_post({
            'params': params
        });
    }

    /**
     * Gets the search key
     * @return {string} search key
     */
    get_key(){
        let key = $(this.selectors['search_input']).val();
        if(key == '') {
            if(window.location.pathname == '/search') this.error('');
            else this.error('Error: Empty search...');
        }

        key = key.replace('/', '');

        this.key = key;
        return key;
    }

    /**
     * Generates a new search url
     * Example: /search/die%20hard&cats=[unknown,documents,movies,music,pictures]&proto=[ftp,http,smb]&type=both&size=134217728-536870912&exts=[mp3]
     * @param {Object} [params] - the data to be used in url crafting
     * @return {string} url
     */
    get_url(params){
        if (!params) params = this._gather_params('urls');

        let url = `${this.application_root}search/${this.get_key()}`;

        $.each(['file_categories', 'file_type', 'file_size', 'file_extensions'], function(index, key){
            if(params.hasOwnProperty(key)){
                url += params[key];
            }
        });

        return url;
    }

    /**
     * Sets the browser URL bar
     * @param {string} url - the url
     */
    static set_urlbar(url){
        history.pushState({}, null, url);
    }

    /**
     * Gets filter data from the browser URL bar
     * @return {Object} params
     */
    static get_urlbar(){
        let params = {};

        let val = document.location.href.substr(document.location.href.indexOf('/search') + 7);
        if(val == '') return {'key': val};
        else val = val.substr(1);

        val.split("&").forEach(function (part, index) {
            let item = part.split("=");
            var obj = [decodeURIComponent(item[0]), decodeURIComponent(item[1])];

            if (index == 0) {
                params['key'] = obj[0];
            } else {
                if(obj[1].startsWith('[') && obj[1].endsWith(']')){
                    // trim first/last chars
                    obj[1] = obj[1].substr(1);
                    obj[1] = obj[1].substring(0, obj[1].length - 1);

                    obj[1] = obj[1].split(",");
                }

                params[obj[0]] = obj[1];
            }
        });

        return params;
    }

    /**
     * Gathers the filters
     * @param {string} key - 'params' returns an `Object` containing POST data for the API search request, 'url' returns an `Object` containing the url parts
     * @return {Object} params
     */
    _gather_params(key){
        let params = {
            'params': {},
            'urls': {}
        };

        let data = this.gather_params();
        let translate = {
            'exts': 'file_extensions',
            'cats': 'file_categories',
            'type': 'file_type',
            'size': 'file_size'
        };

        ['exts', 'cats', 'type'].forEach(function(name){
            if (data[key].hasOwnProperty(name) && data[key][name].length){
                params[key][translate[name]] = data[key][name];
            }
        });

        if(data[key].hasOwnProperty('size') && data[key]['size'] != ''){
            params[key]['file_size'] = data[key]['size'];
        }

        return params[key];
    }

    /**
     * helper function to access `this.selectors`
     * @param {string} key - the key
     * @return {string} the selector value
     */
    selector(key){
        return this.selectors[key];
    }

    /**
     * Contacts the search API
     * @param {Object} [params] - the filters used in the call
     * @param {Function} callback - the callback function
     * @return
     */
    _search_post({params = {}} = {}){
        let url_data = this.get_url();
        Search.set_urlbar(url_data);

        let key = params['key'];
        delete params['key'];

        let _url = `search/${key}`;
        let _data = JSON.stringify(params);

        FindexGui.api(_url, "POST", _data).then(function(data){
            this.parse_results(data);
        }.bind(this));
    }
}
