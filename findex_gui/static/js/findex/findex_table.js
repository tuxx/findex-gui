// Sander Ferdinand sander@cedsys.nl 8/10/2017
// Bootstrap/jQuery table plugin
//
// datatables/dynatables didnt give me enough freedom...
// this should be faster too in terms of drawing rows
//
// Usage: 
//     let table = $("table#resource");
//
//     table.fintable({
//         endpoint: "/resource/get",
//         ui_search: false
//     });


Array.prototype.insert = function ( index, item ) {
    this.splice( index, 0, item );
};

(function ($) {
    $.fn.fintable = function(data){
        let settings = $.extend({
            limit: 10,
            offset: 0,
            page: 1,
            ui_search: true,
            ui_limit: true,
            row_writer: null,
            column_writer: null
        }, data);

        if(!settings.hasOwnProperty("endpoint")){
            throw 'undefined option endpoint';
        }
        return new FinTable(this, settings);
    };
}(jQuery));


class FinTable {
    constructor(target, settings){
        this.table = $(target);
        this.settings = settings;
        this.endpoint = settings.endpoint;

        this.search = null;
        this.limit = settings.limit;
        this.offset = settings.offset;
        this.page = settings.page;

        this._time = 0;
        this._queryRecordCount = -1;
        this._totalRecordCount = -1;

        this.uuid = Math.random()*10;
        this.columns = this.table.find("th").map(
            function(i, obj) {
                return [ $(obj).html().toLowerCase() ];
            }).get();

        this.prepare_html();
        this.draw_header();
        this.draw();
        this._events();
    }

    draw(page, per_page){
        if(typeof page !== 'undefined') this.page = page;
        if(typeof per_page !== 'undefined') this.limit = per_page;
        this.offset = (this.page-1) * this.limit;

        let self = this;
        let data = {
            "offset": this.offset,
            "limit": this.limit,
            "search": this.search
        };

        let date_now = new Date();

        FindexGui.api(this.endpoint, 'GET', data).then(function(resp){
            self._time = (new Date() - date_now);

            if(resp.hasOwnProperty('data') && resp.data.hasOwnProperty('records')) {
                self.clear();
                self._queryRecordCount = resp.data.queryRecordCount;
                self._totalRecordCount = resp.data.totalRecordCount;

                if(!resp.data.records.length || !resp.data.queryRecordCount){
                    self.draw_footer([], "No results");
                    return;
                }

                resp.data.records.forEach(function(obj, i){
                    obj = FinTable._data_normalize(obj);
                    self.draw_row(obj);
                });

                let navigation = self._paginate();
                self.draw_footer(navigation);
            } else {
                self.draw_footer([], "Invalid data")
            }
        }, this);
    }

    static _data_normalize(row_data){
        let _data = {};

        for (let k in row_data) {
            if (row_data.hasOwnProperty(k)) {
                _data[k.toLowerCase().replace("_", " ")] = row_data[k];
            }
        }
        return _data;
    }

    draw_row(row_data){
        let td = [];
        let column_writer = null;
        let row_writer = null;
        if(this.settings.column_writer) column_writer = this.settings.column_writer;
        if(this.settings.row_writer) row_writer = this.settings.row_writer;
        else column_writer = FinTable.draw_column;

        for(let i = 0; i !== this.columns.length; i++){
            let column_name = this.columns[i];

            if(row_writer !== null){
                let value = row_writer(column_name, row_data);
                td.push(value);
            } else {
                let value = "";
                if(row_data.hasOwnProperty(column_name)){
                    value = column_writer(column_name, row_data[column_name]);
                }
                td.push(value);
            }
        }

        let tds = td.map(function(obj){return `<td>${obj}</td>`});
        this.table.find("tbody").append(`<tr>${tds}</tr>`);
    }

    static draw_column(column_name, value){
        return value;
    }

    clear(){
        this.table.find("tbody").empty();
    }

    _paginate(){
        if(this._queryRecordCount === -1 || this._queryRecordCount <= this.limit) return [];
        let total = Math.ceil(this._queryRecordCount / this.limit);
        let current_page = (this.offset / this.limit) + 1;

        let pagination_size = 6;
        let lrsize = Math.ceil(pagination_size / 2);
        let rtn = [];

        for(let x = 1; x !== (total+1); x++){
            if (x >= (current_page - lrsize) && x <= (current_page + lrsize)) {
                rtn.push(x);
            }
        }

        [1, total].forEach(function (value) {
            if(!rtn.includes(value)){
                rtn.insert(0, value);
                rtn.insert(1, '...');
            }
            rtn.reverse();
        });

        return rtn;
    }

    _events(){
        let self = this;
        $(document).on('click', `.fintable[data-fintable='${this.uuid}'] .page-link`, function(){
            let page = $(this).attr('data-page');
            self.draw(parseInt(page));
        });

        if(self.settings.ui_limit) {
            $(`.fintable[data-fintable='${this.uuid}'] select#limit`).on('change', function (e) {
                let val = this.value;
                self.draw(1, parseInt(val));
            });
        }

        if(self.settings.ui_search) {
            $(`.fintable[data-fintable='${this.uuid}'] input#search`).on('input', function (e) {
                let val = this.value;
                if(val.length >= 3){
                    self.search = val;
                    self.draw(1);
                } else {
                    self.search = null;
                    self.draw(1);
                }
            });
        }
    }


    draw_footer(navigation, err){
        let lis = [];
        let self = this;

        navigation.forEach(function(obj, i){
            if(obj === "..."){
                lis += `<li><span class="ellipse">…</span></li>`;
            } else {
                let active = (function() {
                    if(obj === self.page) return ' active';
                    else return '';
                })();

                lis += `<li class="page-item${active}">
                        <a data-page="${obj}" class="page-link" href="#" onClick="return false;">${obj}</a></li>`;
            }
        });

        let html_navigation = `
        <div class="col-xs-8">
            <nav aria-label="Table navigation">
                <ul class="pagination pagination-sm">                
                    ${lis}
                </ul>
            </nav>
        </div>
        `;

        let html_metrics_display = "";
        if(err) html_metrics_display = `<span class="err">${err}</span>`;
        else html_metrics_display = `Display: ${this._totalRecordCount}/${this._queryRecordCount}`;

        let html_metrics = `
        <div class="col-xs-4">
            <span class="metrics pull-right">
            Response: ${this._time}ms
            <br>
            ${html_metrics_display}
            </span>
        </div>
        `;

        let html = html_navigation+html_metrics;
        this.table.find(".fintable-footer").html(html);
    }

    draw_header(){
        let html_ui_limit = '';
        let html_ui_search = '';

        if(this.settings.ui_limit) {
            html_ui_limit = `
            <div class="col-xs-4 pull-left">
                <div class="form-group">
                    <label for="limit">Show: </label>
                    <select id="limit" class="form-control input-sm">
                        <option>10</option>
                        <option>25</option>
                        <option>50</option>
                        <option>100</option>
                    </select>
                </div>
            </div>
            `;
        }

        if(this.settings.ui_search){
            html_ui_search = `
            <div class="col-xs-4 pull-right">
                <div class="input-group fintable-input-group fintable-input-search">
                    <input type="text" id="search" class="form-control input-sm"  placeholder="Search" >
                    <span class="input-group-addon input-sm">
                        <button type="submit">
                            <span class="glyphicon glyphicon-search"></span>
                        </button>
                    </span>
                </div>
            </div>
            `;
        }

        let html =  `
        <form class="form-inline">
            ${html_ui_limit}
            ${html_ui_search}
        </form>
        `;
        this.table.find(".fintable-header").html(html);
    }

    prepare_html(){
        let parent = this.table.parent();
        let table_html = parent.html();
        parent.empty();

        let html = `
        <div class="fintable" data-fintable="${this.uuid}">
            <div class="row fintable-header"></div>
            ${table_html}
            <div class="row fintable-footer"></div>
        </div>`;

        parent.html(html);
        this.table = $(`.fintable[data-fintable='${this.uuid}']`);
    }
}
