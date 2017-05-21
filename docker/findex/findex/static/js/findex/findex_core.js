$('#help').css('display', 'none');



function endsWith(str, suffix) {
    return str.indexOf(suffix, str.length - suffix.length) !== -1;
}

function historyBack(){
    history.back()
}

function file_icons(){
    var file_icons = {
        "bluray": ""
    }
}

function errorBox(errors){
    var text = '';
    for(var i = 0; i != errors.length ; i++){
        text += '<b>' + i + ':</b> ' + errors[i] + '<br>';
    }
    return '<div class=\"alert alert-danger\">'+text+'</div>';
}

function required_input(id){
    $('#'+id).fadeTo(300,0.3);
    setTimeout(function(){$('#'+id).fadeTo(200,1);}, 300);
}

function change_uri(uri){
    window.history.pushState("", "", uri);
}

function goto_uri(uri){
    window.location.href = uri;
}

function check_form(show_errors){
    var warnings = [];
    var data = {};

    $('body *').each(function(){
        var $this = $(this);

        if($this.attr('data-req')){
            var id = $this.attr('id');
            var text = $this.html();

            if($this.attr('data-req') == 'yes' && text == 'Empty'){
                warnings.push('Property \'' + id + '\' cannot be empty.');
                required_input(id);
            }
            else{
                data[id] = text;
            }
        }
    });

    if(warnings.length == 0){
        return data;
    }
    else{
        if(show_alerts) $('#errorbox').html(errorBox(warnings));
    }
}

function chart_browse_pie_filedistribution_spawn(target, data, source_name) {
    var c = $(target).highcharts({
        chart: {
            plotBackgroundColor: null,
            plotBorderWidth: 0,
            plotShadow: false,
            margin: [0, 0, 0, 0],
            spacingTop: 0,
            spacingBottom: 0,
            spacingLeft: 0,
            spacingRight: 0,
            reflow: false
        },
        title: {
            text: '',
            align: 'center',
            verticalAlign: 'middle',
            y: -116
        },
        tooltip: {
            pointFormat: '{series.name}: <b>{point.percentage:.1f}%</b>'
        },
        plotOptions: {
            pie: {
                size: '100%',
                dataLabels: {
                    enabled: true,
                    distance: -40,
                    style: {
                        fontWeight: 'bold',
                        color: 'white',
                        textShadow: '0px 1px 2px black'
                    }
                },
                startAngle: -90,
                endAngle: 90,
                center: ['50%', '58%']
            }
        },
        credits: {
            enabled: false
        },
        series: [{
            type: 'pie',
            name: source_name,
            innerSize: '0%',
            data: data
        }]
    });
    return c;
}

function gets(){
    console.log($('#form_filter').serialize);

}

$.fn.serializeObject = function()
{
    var o = {};
    var a = this.serializeArray();
    $.each(a, function() {
        if (o[this.name] !== undefined) {
            if (!o[this.name].push) {
                o[this.name] = [o[this.name]];
            }
            o[this.name].push(this.value || 'x2');
        } else {
            if(this.value){
                o[this.name] = this.value;
            }

        }
    });
    return o;
};

function url_for(inp){
    if(inp.startsWith("/")) inp = inp.slice(1);
    return `${APPLICATION_ROOT}${inp}`;
}
