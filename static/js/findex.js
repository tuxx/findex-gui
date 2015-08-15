/* menu */

var startMenu = 0;
var menuType = 0;
var menuTotal = 0;
var menuOrder = 0;

$('#menu .menu-item').click(function() {
    if($(this).attr('rel') == menuType) {
        closeMenu();
        menuType = 0;
    } else {
        $('#menu .menu-item').removeClass("active");
        $( "#feed" ).empty();
        $('menu .filter').removeClass( "active");
        $('menu .filter:first').addClass( "active");
        $("menu #dropdown").slideDown('slow', function() {});
        menuTotal = Math.floor(($(document).width()-80)/154);
        $("#feed-container").width(menuTotal*154+88);
        $("#feed-slider").width(menuTotal*154);
        startMenu = 0;
        $(this).addClass("active");
        showMenuFeed(startMenu, $(this).attr('rel'));
        $("menu #dropdown .archive").attr('href', base_url + "magazine/" + menuType);
    }
    return false;
});

$(document).ready(function(){
    function get_file_icon(fileformat){
        var data = {
            0: '/static/img/icons/blue/128/Very_Basic/file-128.png',
            1: '/static/img/icons/blue/128/Very_Basic/document-128.png',
            2: '/static/img/icons/blue/128/Photo_Video/film-128.png',
            3: '/static/img/icons/blue/128/Very_Basic/music-128.png',
            4: '/static/img/icons/blue/128/Very_Basic/picture-128.png'
        };

        return data[fileformat];
    }

    //
    //    MENU SEARCH DROPDOWN
    //

    // vars
    $('.menu_dropdown').hide();
    var menu_searchdropbox_expended = false;
    var menu_search_lastquery = '';

    //events
//    $('.menu_dropdown_item').click(function(){
//        var href = $(this).attr('id');
//        console.log(href);
//        //goto_uri(href);
//    });

    //functions
    function menu_search_do(search_query){
        $.ajax({
            type: 'POST',
            url: '/post',
            data: 'cmd=menu_search_dropdown&val=' + search_query,
            dataType: 'json',
            success: function(res){
                menu_search_callback(res)
            },
            error:function(zemmel){

            }
        });
    }

    $('.menu_dropdown').mouseout(function(){
        $(document).one('click',function() { $('.menu_dropdown').fadeOut(200); });
    });

    function menu_search_callback(result) {
        $('.menu_dropdown').empty();

        if (result.hasOwnProperty('menu_search_dropdown')) {
            if (result['menu_search_dropdown'] == 'OK') {
                var data = result['data'];
                var search_val = result['menu_search_dropdown'];

                if (data.length > 0) {
                    for (var i = 0; i != data.length; i++) {
                        var file_name = data[i]['file_name'];
                        var file_format = data[i]['file_format'];
                        var file_query = data[i]['search_val'];
                        var file_size = data[i]['file_size'];
                        var host = data[i]['host'];
                        var href = data[i]['href'];

                        var file_icon = get_file_icon(file_format);

                        if (file_name.length >= 55) {
                            file_name = 'too long to display';
                        }

                        var bgcolor = '';
                        if (i % 2 == 0) {
                            bgcolor = " tint";
                        }
                        else {
                            bgcolor = "";
                        }

                        $('.menu_dropdown').append('<a href=\"/browse' + href + '\" class=\"menu_dropdown_item clickable' + bgcolor + '\"><div class=\"menu_dropdown_item_thumbnail\"><img style=\"margin-top:5px;\" src=\"' + file_icon + '\" width=\"30px\"/></div><div class=\"menu_dropdown_item_description\"><span class=\"menu_dropdown_item_filename\">' + file_name + '</span><br><b>' + file_size + '</b> | ' + host + '</div></a>');
                    }

                    $('.menu_dropdown').append('<center><small>Press Enter for more search results.</small></center>');
                }
                else {
                    $('.menu_dropdown').append('<center>No results.</center>');
                }
            }
        }
    }

    function search_dropbox_toggle(){
        if (!menu_searchdropbox_expended){
            $('.menu_dropdown').show();
            menu_searchdropbox_expended = true;
        }
        else{
            $('.menu_dropdown').hide();
            menu_searchdropbox_expended = false;
        }
    }

    function dropbox_search(){
        if(!menu_searchdropbox_expended){
                search_dropbox_toggle();
        }

        $('.menu_dropdown').empty();
        $('.menu_dropdown').append("<div class=\"menu_dropdown_item\"><center><img src=\"/static/img/loader.gif\"/></div></center></div>");
        menu_search_do($('#menu_searchbar').val());
    }

    $("#menu_searchbar").keyup(function (e) {
        if (e.keyCode == 13){
            var val = $('#menu_searchbar').val();

            if(val != ''){
                var uri = '/search?key='+val+'&server=[*]&protocol=[*]';
                goto_uri(uri);
            }
        }
        else {
            var val = $('#menu_searchbar').val();
            if ( val != '' && val.length >= 4 ){
                if(menu_search_lastquery != val){
                    $('.menu_dropdown').show();
                    menu_search_lastquery = val;
                    dropbox_search();
                }
            }
            else {
                $('.menu_dropdown').hide();
                menu_searchdropbox_expended = false;
            }
        }
    });

    $('.menu_dropdown_item').hover(function(){
        $(this).css('background-color','#f5f5f5');
    }, function(){
        $(this).css('background-color', 'transparent');
    });

    $('#menu_searchbar').focus(function()
    {
        /*to make this flexible, I'm storing the current width in an attribute*/
        $(this).attr('data-default', $(this).width());
        $(this).animate({ width: 250 }, 'fast');
    }).blur(function()
    {
        if ($(this).val() == ""){
            /* lookup the original width */
            $(this).animate({ width: 100 }, 'fast');
        }
    });

    $(".menu_item").on('mouseenter',function(){
      var cls = $(this).attr("class");

      if (endsWith(cls, "menu_btn")){
        //$(this).animate({"marginTop": "-2px"}, "fast");
        //$(this).css({"background": "red", "color": "white"});
      }

    });
    $(".menu_item").on('mouseleave',function(){
      //$(this).animate({"marginTop": "0px"}, "fast");
    });
});