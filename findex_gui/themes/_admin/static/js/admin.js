$(function(){
    // Collapse sidebar menu on the currently active item
    var document_location_pathname = document.location.pathname.replace('#', '');
    var menu_selection = $('.sidebar-menu [href="'+document_location_pathname+'"]');
    menu_selection.parent().parent().parent().addClass('active');
    menu_selection.parent().addClass('active');
});

function msgbox_error(msg){
    $("div.box-body").prepend(`
    <div class="col-xs-4 no-padding">
        <div class="alert alert-danger alert-dismissible">
            <button type="button" class="close" data-dismiss="alert" aria-hidden="true">×</button>
            <h4><i class="icon fa fa-ban"></i> Error!</h4>
            ${msg}
        </div>
    </div>
    `);
}