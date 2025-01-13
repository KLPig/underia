var href = window.location.href;
var gets = href.split('?');
var filter = '';
if (gets.length > 1) {
    var params = gets[1].split('&');
    for (var i = 0; i < params.length; i++) {
        var param = params[i].split('=');
        if (param[0] == 'filter') {
            filter = param[1];
        } else if (param[0] == 'filter-item') {
            filter = param[1] + '-filter';
        }
    }
}
var found = false;
if (filter != '') {
    var items = document.getElementsByClassName('item-row');
    for (var i = 0; i < items.length; i++) {
        if (items[i].id == filter) found = true;
        else items[i].style.display = 'none';

    }
}
document.getElementsByTagName('body')[0].innerHTML += "" +
"<div style='position: fixed; top: 0; left: 0;' class='filter-container'>" +
"<form action='?filter-item=' method='get'>" +
"<input type='text' name='filter-item' placeholder='Filter' value=''>" +
"</form>" +
"<button onclick='location.href=\"?nofilter=true\"'>Clear Filter</button>"
"</div>" +
""
if (!found) {
    document.getElementById('item-table').innerHTML += '<tr><td colspan="5" class="text-center"><h1>No items found.</h1></td></tr>';
}
if (filter != '') {
    document.getElementById('item-table').innerHTML += '<tr><td colspan="5" class="text-center"><a href="?nofilter=true">Show All</a></td></tr>';
}