function alert_show(msg, status) {
    $('.alert_show').remove();
    $('body').append('<div class="alert alert_show ' + status + '">' + msg + '</div>');
    setTimeout(function() {
        $('.alert_show').slideUp();
    }, 3000);
    setTimeout(function() {
        $('.alert_show').remove();
    }, 4000);
}
function pn(no){
    var n = no + '';
    n = n.replace(/1/g, '۱');
    n = n.replace(/2/g, '۲');
    n = n.replace(/3/g, '۳');
    n = n.replace(/4/g, '۴');
    n = n.replace(/5/g, '۵');
    n = n.replace(/6/g, '۶');
    n = n.replace(/7/g, '۷');
    n = n.replace(/8/g, '۸');
    n = n.replace(/9/g, '۹');
    n = n.replace(/0/g, '۰');
    return n;
}
function en(no){
    var n = no + '';
    n = n.replace(/۱/g, '1');
    n = n.replace(/۲/g, '2');
    n = n.replace(/۳/g, '3');
    n = n.replace(/۴/g, '4');
    n = n.replace(/۵/g, '5');
    n = n.replace(/۶/g, '6');
    n = n.replace(/۷/g, '7');
    n = n.replace(/۸/g, '8');
    n = n.replace(/۹/g, '9');
    n = n.replace(/۰/g, '0');
    return n;
}

var feedobj = $('#feed');
var loadingobj ;
var a_url = a_url || "";
var extend_query = extend_query || "";
var disable_masonry = disable_masonry || 0 ;
if (disable_masonry==0){
    feedobj.masonry({
        itemSelector : '.feed-item',
        isRTL: true,
        isResizeBound: false,
        isAnimated: false,
        isFitWidth: true
    });
}

var next_pref = next_pref || '?older=';

function load_posts(page) {
    $('.footer-loading-box').show(0);
    $.get(a_url + next_pref + page + '&'+extend_query,function(response) {
        if(response==0){
            loadingobj.hide();
        }else{
            var boxes = $(response);
            feedobj.append( boxes ).masonry( 'appended', boxes );
            feedobj.masonry('reload');
            loadingobj.hide();
            start_loading=0;
            ana_ajax(a_url + next_pref + page + '&'+extend_query);
        }
    }).done(function(d) {
        $('.footer-loading-box').hide(0);
    })
    .fail(function(d) {
        $("#next_url").addClass("btn btn-success").html('کلیک کنید');
    })
    .always(function(d) {
        $('.footer-loading-box').hide(0);
    });
    feedobj.masonry('reload');
}


$(window).scroll(function() {
    var sc = $(window).scrollTop();
    if (sc > 300) {
        $('.gotop').css('display', 'block');
    }else{
        $('.gotop').css('display', 'none');
    }

    loadingobj = $('.footer-loading-box');
    var break_point = $(document).height() - ($(window).height() * 2.02);
    if ($(window).scrollTop() >= break_point) {
        var next_page = $('#feed span:last').attr('data-next');
        if (next_page && start_loading==0) {
            start_loading=1;
            loadingobj.show();
            load_posts(next_page);
            live_content();
            if (typeof live_content_user == 'function'){
                live_content_user();
            }
        }
    }
});

function readURL(input, img_id) {
    var d = '';
    if (input.files && input.files[0]) {
        var reader = new FileReader();

        reader.onload = function (e) {
            $('#'+img_id).attr('src', e.target.result);
        }
        reader.readAsDataURL(input.files[0]);
    }
}

var isVisible = false;
var clickedAway = false;
var notifCache=false;


$('.tooltips').tooltip();
$('body').on('click', '#ScrollToTop', function(event) {
    event.preventDefault();
    $('html, body').animate({scrollTop: $("#wrapper").offset().top}, 1000);
});


$(".popnotify").bind('click', function(){
    var el=$(this);
    el.parent().children('.loading-img').show();

    if (isVisible){
        $(el).popover('hide');
    }else{
        isVisible = true;
        if(!notifCache){
            $.get( el.attr('data-load'), function(d) {
                notifCache=d;
            })
            .done(function(d) {
                el.unbind('click').popover({
                    content: d,
                    title: "notifications",
                    placement:'bottom',
                    html:true
                }).popover('show');
                el.parent().children('.loading-img').hide(0);
            })
            .fail(function(d) {
                alert( "error" );
            })
            .always(function(d) {
            });
        }else{
            el.unbind('click').popover({
                content: notifCache, 
                title: "notifications",
                placement:'bottom',
                html:true
            }).popover('show');    
            el.parent().children('.loading-img').hide(0);
        }
    }
});

$('body').on('click', '.popover-close', function(event) {
    event.preventDefault();
    var id = $(this).parents('.popover').attr('id');
    $('#'+id).popover('hide');
});

function live_content(){
    $('#pinitem').on('hide', function() {
        $(this).removeData('modal');
        $(this).children('.modal-body').html('');
    });

    $('.feed-item').on({
        mouseenter:
        function(){
            $(".feed-actions", this).stop().animate({top:'5px'},{queue:false,duration:160});
        },
        mouseleave:
        function(){
            $(".feed-actions", this).removeAttr('style');
            $(".feed-actions", this).stop().animate({},{queue:false,duration:160});
        }
    });
}

$('.topuser-thumb').webuiPopover('destroy').webuiPopover({
    trigger: 'hover',
    width: 300,
    delay: {
        show: 0,
        hide: 1000
    }
});

$('body').on('click', '.login_required', function(event) {
    event.preventDefault();
    alertify.error("ابتدا وارد حساب کاربری خود شوید");
    return false;
});

function marker(t){
    var p = t.position();
    var w = t.width();
    $('.marker').show(0).css('left', p.left + (w / 2) - 4 +'px');
}



$(function () {
    $('body').on('click', '.upload_img_btn', function(event) {
        event.preventDefault();
        $('#id_avatar').click();
    });

    $('body').on('click', '.gotop', function(event) {
        event.preventDefault();
        $('html, body').animate({ scrollTop: 0 }, 'normal');
    });

    $('form[data-async]').on('submit', function(event) {
        var $form = $(this);
        var $target = $($form.attr('data-target'));

        $.ajax({
            type: $form.attr('method'),
            url: $form.attr('action'),
            data: $form.serialize(),

            success: function(data, status) {
                alert(data);
                $('#pinitem').modal('hide').children('.modal-body').html('');
                
            }
        });

        event.preventDefault();
    });

    $('body').on('change', '#id_avatar', function(event) {
        event.preventDefault();
        readURL(this, 'avatar_img');
    });

    $('body').on('click', '.load-follow', function(event) {
        event.preventDefault();
        var t = $(this);
        t.children('img').css('display', 'inline-block');
        var next_page = $('.user-username a:last').attr('data-next');
        $.ajax({
            url: t.attr('href'),
            type: 'POST',
            data: {'older': next_page}
        })
        .done(function(response) {
            if (response == '0') {
                t.addClass('disabled');
                alertify.error("مورد بیشتری پیدا نشد");
            }else{
                $('#follower-box').append(response);
            }
        })
        .fail(function() {
            alertify.error("خطا. با مدیر تماس بگیرید");
        })
        .always(function() {
            t.children('img').css('display', 'none');
        });
        return false;
    });

    //
    $('[data-toggle="tooltip"]').tooltip();
    $('.menu-box ul li.parent').attr('data-content', '');

    $('body').on('click', '.menu-box ul li.parent > a', function(event) {
        event.preventDefault();
        p = $(this).parent();
        if (p.attr('collapse') == 'true') {
            p.removeAttr('collapse');
            p.children('ul').slideUp('100');
            p.attr('data-content', "");
        } else {
            p.parent().children('li').removeAttr('collapse');
            p.parent().children('li').children('ul').slideUp('100');
            $(this).parent().attr('collapse', 'true');
            $(this).parent().children('ul').slideDown('100');
            p.attr('data-content', "");

        }
    });

    $('body').on('click', '.menu-box .colse-menu-btn', function(event) {
        event.preventDefault();
        $('.menu-box').hide('fast');
    });

    $('body').on('click', '.resp-menu', function(event) {
        event.preventDefault();
        $('.menu-box').css('display', 'block');
        $('.menu-box').animate({
            width: 320},
            100, function() {});
    });

    $('body').on('mouseleave', '#wis_navbar', function(event) {
        $(".marker").hide();
    });
    
    $('body').on('mouseenter', '#wis_navbar > ul > li', function(event) {
        event.preventDefault();
        var t = $(this);
        marker(t);
    });

    $('body').on('click', '#wis_navbar > ul > li', function(event) {
        event.preventDefault();
        var t = $(this);
        var ul = $(this).parent('ul');
        if(t.children('ul').length != 0){
            if (t.hasClass('open')) {
                t.removeClass('open');
                $('.marker').css('display', 'none');
                t.children('ul').stop(true, false).slideUp('fast');
            }else{
                $('#wis_navbar > ul > li').removeClass('open');
                $('#wis_navbar > ul > li > ul').stop(true, false).slideUp('fast');
                t.addClass('open');
                if (t.hasClass('cats')) {
                    t.children('ul').stop(true, false).slideDown('fast').css('display', 'flex');
                }else{
                    t.children('ul').stop(true, false).slideDown('fast').css({
                        display: 'flex',
                        flexDirection: 'column'
                    });
                }
            }
        }else{
            window.location.href = $(this).children('a').attr('href');
        }
    })
    $('body').on('click', '#wis_navbar > ul > li.cats ul li', function(event) {
        return false;
    });
    $('body').on('click', '#wis_navbar > ul > li > ul > li > a', function(event) {
        window.location.href = $(this).attr('href');
    });

    // $('body').on('mouseleave', '#wis_navbar', function(event) {
    //     $('.marker').css('display', 'none');
    // });

    //
    $('body').on('click', '.cats > ul > li', function(event) {
        event.preventDefault();
        var t = $(this);
        var ch = t.children('ul.sub-cats');
        if (t.hasClass('open')) {
            t.removeClass('open');
            ch.stop(true, false).slideUp('fast');
        }else{
            $('.cats > ul > li.parent').removeClass('open');
            $('.sub-cats').stop(true, false).slideUp('fast');
            t.addClass('open');
            t.children('ul.sub-cats').slideDown('fast');
        }
    });
    $('body').on('click', '.sub-cats a', function(event) {
        window.location.href = $(this).attr('href');
    });

    var l = $('.cats > ul > li');
    l.width(100/l.length+'%');

    var l = $('body > .container-fluid .cats > ul > li');
    l.each(function(index, el) {
        $(this).width(100/l.length+'%');
    });

    $('body').on('click', '.only_mobile_view .fa-times', function(event) {
        event.preventDefault();
        $(this).parents(".only_mobile_view").remove();
        $('body').css('padding-top', "0 !important");
        $('body').append("<style type='text/css'>@media (max-width: 768px) {body{padding-top:0 !important;}}</style>");
        var date = new Date();
        date.setTime(date.getTime() + (60 * 60 * 1000));
        Cookies.set('no_download', 1, { expires : date });
    });

    var no_download = Cookies.get('no_download');

    if (no_download) {
        $('.top_download').parent().remove();
        $('body').append("<style type='text/css'>@media (max-width: 768px) {body{padding-top:0 !important;}}</style>");
    };

});

live_content();

