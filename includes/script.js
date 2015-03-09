$(document).ready(function() {
    $('div.description').hide();
    $('h2 label').after($('<span/>').addClass('more').html('&nbsp;[...]'));
    $('span.more').toggle(
            function() {
                $(this).parent().next('div.description').slideDown();
            },
            function() {
                $(this).parent().next('div.description').slideUp();
            });
    $('form').submit(function() { return false; });
    $(':input:submit').hide();
    $(':checkbox').change(postAsync);
    $(':checkbox').iphoneStyle({ checkedLabel: 'Ja', uncheckedLabel: 'Nei' });
});

function postAsync() {
    selectedIds = [];
    $(':checkbox:checked').each(function(n, checkbox) {
        selectedIds.push($(this).attr('value'));
    });
    $.ajax({
        url : $('form').attr('action'),
        type : 'POST',
        data: { 'session' : selectedIds, redirect : false },
        cache: false,
        error: function(XMLHttpRequest, status, cause) {

        }
    });
}
