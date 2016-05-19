$(function(){
    // Collapse sidebar menu on the currently active item
    var document_location_pathname = document.location.pathname.replace('#', '');
    var menu_selection = $('.sidebar-menu [href="'+document_location_pathname+'"]');
    menu_selection.parent().parent().parent().addClass('active');
    menu_selection.parent().addClass('active');
});
