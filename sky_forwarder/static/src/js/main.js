(function () {
'use strict';

$(document).ready(function(){

    $("img.gan_giao_nhan").click(function(){
        var id = $(this).data('id');
        var nhanvien_id = $(this).data('nhan-vien-id');
        document.getElementById('tp-gan-nv-' + id + '-' + nhanvien_id).submit();
    });

    var page = $('.tgl_page').data('value');

    $('#page-' + page).addClass('active');

});


}());
