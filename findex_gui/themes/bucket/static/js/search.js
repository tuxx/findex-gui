class bucket_search extends Search {
    constructor(application_root, autocomplete, per_page, selectors) {
        super(application_root, autocomplete, per_page, selectors);

        this.icons = {
            "d": url_for("/static/themes/bucket/static/img/icons/folder-128.png"),
            "0": url_for("/static/themes/bucket/static/img/icons/file-128.png"),
            "1": url_for("/static/themes/bucket/static/img/icons/document-128.png"),
            "2": url_for("/static/themes/bucket/static/img/icons/film-128.png"),
            "3": url_for("/static/themes/bucket/static/img/icons/music-128.png"),
            "4": url_for("/static/themes/bucket/static/img/icons/picture-128.png")
        };

        this.key = '';
        this._loading = false;

        // On page-load, parse the filters present in the URL bar and do some front-end work
        let url_params = Search.get_urlbar();
        this.parse_urlbar(url_params);
    }

    /* Required */
    parse_results(data){
        if(!data.hasOwnProperty("data")){
            bucket_search.error("Something went wrong");
            throw "bleh";
        }

        if(!data.status){
            bucket_search.error(data.data);
            throw "bleh";
        }

        data = data.data;

        if(!this._loading){
            this._loading = true;
        }

        let sel_results_container = this.selectors['search_results'];

        // Below clauses will update global var `search_results` based on different scenarios
        if(Object.keys(search_results).length == 0 && search_results.constructor === Object){
            search_results = jQuery.extend(true, {}, data);
        } else if(data['params']['key'] != search_results['params']['key']) {
            // results came in with a new key
            search_results = jQuery.extend(true, {}, data);
            $(sel_results_container).html('');
        } else if (data.params.page == 0 && data.results.length == 0) {
            $(sel_results_container).html('');
            $(sel_results_container).append(`<span id="no_more_results">no results</span>`);
            return;
        } else if(search_results['results'].length > 0 && data['results'].length == 0) {
            // hit end of search
            $(sel_results_container).append(`<span id="no_more_results">no more results</span>`);
            exhausted_results = true;

            this.toggle_loading(this);
            return;
        } else  {
            // new additions due to page scroll - need to update the results
            let old_results = search_results['results'];
            search_results = jQuery.extend(true, {}, data);
            search_results['results'] = search_results['results'].concat(old_results);
        }

        // assign html
        bucket_search.set_result_html(data, this);

        // assign icons
        bucket_search.set_result_icons(this.icons);

        // highlight search results
        $(sel_results_container).highlight(this.key, { className: 'important' });

        // update title header
        $('#search_col h3#search_header').text(`Results for "${data['params']['key']}"`);

        // toggle the loading indication(s)
        this.toggle_loading();
    }

    static set_result_html(data, context){
        let sel_results_container = context.selectors['search_results'];

        if(data['params']['page'] == 0){
            $(sel_results_container).html('');
        }

        if(search_display_view == 'fancy') {
            $.each(data['results'], function(index, obj) {
                let result = obj;

                $(sel_results_container).append(`
                    <li class="iterable-item">
                        <article class="summary">
                            <a class="avatar-link" href="/"> <span class="avatar avatar-medium">
                              <span class="avatar-inner">
                                <img src="${url_for("/static/img/default_thumbnail.png")}" data-file_isdir="${result['file_isdir']}" data-file_format="${result['file_format']}" title="">
                              </span> </span>
                            </a>

                            <h1><a class="result-link" href="${"/browse/"+result['path_file']}">${result['file_name_human']}</a></h1>

                            <p> Path: <a href="${"/browse/"+result['path_dir']}" rel="nofollow"> ${result['file_path']} </a></p>
                            <ul class="result-metadata clearfix">
                                <li><a href="http://${result['resource']['address']}">${result['resource']['address']}</a></li>
                                <li><a href="${result['path_direct']}"> direct link </a></li>
                                <li>
                                    <span style="margin-right:6px">${result['file_size_human']}</span>
                                    <span>modified
                                        <time datetime="${result['file_modified']}">${result['file_modified_human']}</time>
                                    </span>
                                </li>
                            </ul>
                        </article>
                    </li>
                `);
            });

        } else if(search_display_view == 'table'){
            let buffer = '';

            let sel_table_body = $(sel_results_container).find('table.results_table tbody');
            if(!sel_table_body.length){
                $(sel_results_container).append(`
                    <div class="table-responsive">
                        <table class="results_table table">
                            <thead>
                            <tr>
                                <th id="name">File <i class="fa fa-sort" aria-hidden="true"></i></th>
                                <th id="path">Path <i class="fa fa-sort" aria-hidden="true"></i></th>
                                <th style="min-width: 64px;" id="size">Size <i class="fa fa-sort" aria-hidden="true"></i></th>
                                <th id="modified">Modified <i class="fa fa-sort" aria-hidden="true"></i></th>
                                <th id="address">Server</i></th>
                                <th id="direct">Direct</th>
                            </tr>
                            </thead>
                            <tbody>
                            </tbody>
                        </table>
                    </div>
                `);

                sel_table_body = $(sel_results_container).find('table.results_table tbody')
            }

            let file_max_length = 60;
            let path_max_length = 40;

            $.each(data['results'], function(index, obj) {
                let result = obj;

                let file_name = result['file_name_human'];
                let file_path = result['file_path'];
                let file_modified_human = result['file_modified_human'];

                if(result['file_name'].length > file_max_length){
                    file_name = file_name.substr(0, file_max_length) + '...';
                }


                if(result['file_path'].length > path_max_length){
                    file_path = file_path.substr(0, path_max_length) + '...';
                }

                file_modified_human = file_modified_human.split(' ');
                file_modified_human = `${file_modified_human[1]} ${file_modified_human[2]}`;

                buffer += `
                <tr class="clickable" data-id="" data-href="/browse/${result['file_name_human']}" rel="popover" title="">
                    <td>
                        <img id="file_icon" src="${url_for("/static/img/default_thumbnail.png")}" data-file_isdir="${result['file_isdir']}" data-file_format="${result['file_format']}" title="">
                        <a href="${url_for("/browse/"+result['path_file'])}">
                            ${file_name}
                        </a>
                    </td>

                    <td>
                        <a href="${url_for("/browse/"+result['path_dir'])}">
                            ${file_path}
                        </a>
                    </td>
                    <td><b>${result['file_size_human']}</b></td>
                    <td id="modified">${file_modified_human}</td>
                    <td id="address">${result['resource']['address']}</td>
                    <td id="direct"><a href="${result['path_direct']}">Link</a></td>
                </tr>`;
            });

            $(sel_table_body).append(buffer);
        } else {
            return 'neither fancy or table display? :(';
        }
    }

    /**
     * Loop result tags, set icon based on the attribute `data-file_format`
     * param {Object} [icons] - An object of icons
     */
    static set_result_icons(icons){
        if(!icons) icons = this.icons;

        $('*[data-file_format]').each(function(){
            let file_format = $(this).attr('data-file_format');
            let file_isdir = $(this).attr('data-file_isdir');

            if(file_isdir == 'true'){
                $(this).attr('src', icons['d']);
            } else {
                $(this).attr('src', icons[file_format]);
            }
        });
    }

    set_key(key){
        this.key = key;
        if(key != '') $(super.selector('search_input')).val(this.key);
    }

    /**
     * Sets the front-end to match whatever filters there are in the urlbar
     * param {Object} params - see output of `Search.get_urlbar`
     */
    parse_urlbar(params){
        this.set_key(params['key']);
        if(params['key'] == '') return;

        let filters = ['cats', 'type'];

        filters.forEach(function(key){
            if(params.hasOwnProperty(key)) {
                let menu_label = $(`#sidebar button#${key}`);
                menu_label.text('');

                if(params[key].constructor === Array){
                    params[key].forEach(function(name) {
                        $(`input[type="checkbox"][name="${key}"][data-name="${name}"]`).each(function() {
                            $(this).prop('checked', true);

                            var item_text = $(this).parent().find('label').text();
                            menu_label.append(item_text + ', ');

                            $(this).closest('.btn-group').find('button').addClass('btn-group-active');
                        });
                    });

                    menu_label.text(menu_label.text().slice(0, -2));
                } else {
                    $(`input[type="checkbox"][name="${key}"][value="${params[key]}"]`).each(function() {
                        $(this).prop('checked', true);

                        let item_text = $(this).parent().find('label').text();
                        menu_label.text(item_text);

                        $(this).closest('.btn-group').find('button').addClass('btn-group-active');
                    });
                }

            }
        });

        if(params.hasOwnProperty('exts')){
            params['exts'].forEach(function(name){
                $('#tag1').addTag(name);
            });
        }

        if(params.hasOwnProperty('size')){
            let size = params['size'].split('-');
            let slider = $('#size')[0].noUiSlider;
            if(size[1] == '*') size[1] = slider.options.range.max;

            slider.set([size[0], size[1]]);
        }

        this.search();
    }

    /**
     * Looks at the HTML and gathers the filters
     * @return {Object} An object containing 'params' and 'urls'. Read the comments for more information.
     */
    gather_params(){
        // What we want to return eventually
        let params = {};
        let urls = {};

        // Get the file_categories and file_types from the front-end
        ['cats', 'type'].forEach(function(name){
            let param_url = '';
            let param = [];
            // For each checked menu item ...
            $(`#leftCol`).find(`div#${name} input:checked`).each(function(){
                // Build the URL
                param_url += $(this).attr('data-name') + ",";

                // Build the param
                param.push($(this).attr('data-name'));
            });

            if(param_url != ''){
                param_url = param_url.substring(0, param_url.length - 1);
                param_url = `&${name}=[${param_url}]`;
            }

            // Append both to the returning variables
            urls[name] = param_url;
            params[name] = param;
        });

        // file extensions
        ['exts'].forEach(function(name){
            let param_url = '';
            let param = [];

            $(`div#extensions .tag span`).each(function(){
                var val = $(this).text().trim();

                param_url += val + ",";
                param.push(val);
            });

            if(param_url != ''){
                param_url = param_url.substring(0, param_url.length - 1);
                param_url = `&${name}=[${param_url}]`;
            }

            urls[name] = param_url;
            params[name] = param
        });

        let param_url = '';
        let param = [];

        let slider = $('#leftCol #size')[0].noUiSlider;
        let size = slider.get(false);

        size[0] = parseInt(size[0]);
        size[1] = parseInt(size[1]);

        if (size[0] != 0 || size[1] != slider.options.range.max){
            if(size[1] == slider.options.range.max){
                size[1] = '*';
            }

            let tmp = `${size[0]}-${size[1]}`;

            param_url = `&size=${tmp}`;
            param = tmp;
        }

        urls['size'] = param_url;
        params['size'] = param;

        return {
            'params': params,
            'urls': urls
        }
    }

    toggle_loading(){
        if(this._loading) {
            $('div#search_col').stop().fadeTo(200, 1);
            this._loading = false;
        } else {
            $('div#search_col').stop().fadeTo(200, 0.5);
            this._loading = true;
        }
    }

    error(msg){
        let val = null;
        if(typeof msg === "object"){
            if(msg.hasOwnProperty("data")) {
                val = msg.data;
            } else if(msg.hasOwnProperty("responseText")){
                try {
                    val = JSON.parse(msg.responseText);
                    if(val.hasOwnProperty("data")){
                        val = val.data;
                    } else {
                        throw(":(");
                    }
                } catch (e) {
                    val = msg.responseText;
                }

            } else {
                debugger;
                val = "Could not get repr for type Object";
            }
        } else {
            val = msg;
        }

        $('#search_header').html(`
        <span style="color:red">Error: </span> <small>${val}</small>
        `);
    }
}
