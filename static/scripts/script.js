$(document).ready(function() {
    $('#chosen-select').change(function() {
        var url = $(this).val();
        if (url) {
            $('#formu').attr('action', url);
            $('#content').load(url);
        }
        return false;
    });
});
