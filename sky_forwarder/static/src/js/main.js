(function () {
'use strict';

$(document).ready(function(){


    // Xu ly phan trang

    var listElement = $('#newStuff');

    var perPage = 40; 
    var numItems = listElement.children().length;
    var numPages = Math.ceil(numItems/perPage);

    $('.pager').data("curr",0);

    var curr = 0;
    while(numPages > curr){
      $('<li><a href="#" class="page_link">'+(curr+1)+'</a></li>').appendTo('.pager');
      curr++;
    }

    $('.pager .page_link:first').addClass('active');

    listElement.children().css('display', 'none');
    listElement.children().slice(0, perPage).css('display', 'block');

    $('.pager li a').click(function(){
      var clickedPage = $(this).html().valueOf() - 1;
      goTo(clickedPage,perPage);
    });

    function previous(){
      var goToPage = parseInt($('.pager').data("curr")) - 1;
      if($('.active').prev('.page_link').length==true){
        goTo(goToPage);
      }
    }

    function next(){
      goToPage = parseInt($('.pager').data("curr")) + 1;
      if($('.active_page').next('.page_link').length==true){
        goTo(goToPage);
      }
    }

    function goTo(page){
      var startAt = page * perPage,
        endOn = startAt + perPage;
      
      listElement.children().css('display','none').slice(startAt, endOn).css('display','block');
      $('.pager').attr("curr",page);
    }

    // ket thuc xu ly phan trang

    $("img.gan_giao_nhan").click(function(){
        var id = $(this).data('id');
        var nhanvien_id = $(this).data('nhan-vien-id');
        // console.log(id, nhanvien_id);
        // console.log(document.getElementById(id).submit());
        console.log(document.getElementById('tp-gan-nv-' + id + '-' + nhanvien_id).submit());

    });
});


}());
