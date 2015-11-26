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

var feedobj = $('#feed');
var loadingobj ;
var a_url = a_url || "";
var extend_query = extend_query || "";
var disable_masonry = disable_masonry || 0 ;
// var start_loading = 0;
if (disable_masonry==0){
    feedobj.masonry({
        itemSelector : '.feed-item',
        isRTL: true,
        isResizeBound: false,
        isAnimated: false,
        isFitWidth: true,
    });
}

var next_pref = next_pref || '?older=';

function load_posts(page) {
    $('.footer-loading-box').show(0);
    $.get(
        a_url + next_pref + page + '&'+extend_query,
        function(response) {
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
    }


    $(window).scroll(function() {
        var sc = $(window).scrollTop();
        if (sc > 300) {
            $('.gotop').css('display', 'block');
        }else{
            $('.gotop').css('display', 'none');
        }

        loadingobj = $(".loading");
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


//second
jQuery(function($) {
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

    
});

// for notification popover
var isVisible = false;
var clickedAway = false;
var notifCache=false;


// all footers
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
                    title: "test",
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
                title: "test",
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

$('body').on('click', '.del-comment', function(event) {
    event.preventDefault();
    var t = $(this);
    var href = t.attr('href');
    $.ajax({
        url: href,
    })
    .done(function(res) {
        if (res.status === true) {
            alert_show(res.message, 'success');
            t.parents('.cmnt_item').slideUp('fast');
        }else{
            alert_show('خطا در حذف دیدگاه', 'error');
        }
    })
    .fail(function() {
        alert_show('خطا در حذف دیدگاه', 'error');
    });
    return false;
});

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
    alert_show('ابتدا وارد حساب کاربری خود شوید', 'error');
    return false;
});

function marker(t){
    var p = t.position();
    var w = t.width();
    console.log(p.left + (w / 2) + 4);
    $('.marker').show(0).css('left', p.left + (w / 2) - 4 +'px');
}



$(function () {
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
                alert_show('مورد بیشتری پیدا نشد', 'error');
            }else{
                t.remove();
                $('#follower-box').append(response);
            }
        })
        .fail(function() {
            alert_show('خطا. با مدیر تماس بگیرید');
        })
        .always(function() {
            t.children('img').css('display', 'none');
        });
        return false;
    });


    $('body').on('click', '.ajax-follow', function(event) {
        event.preventDefault();
        var t = $(this);
        var href = t.attr('href');

        $.ajax({
            url: href,
            async: false
        })
        .done(function(response) {
            if (response.status) {
                alert_show(response.message, 'success');
                t.attr('href', '/pin/follow/'+t.data('user-id')+'/0/');
                t.html('قطع ارتباط <i class="fa fa-times"></i>').removeClass('green').addClass('red');
            }else{
                alert_show(response.message, 'success');
                t.attr('href', '/pin/follow/'+t.data('user-id')+'/1/');
                t.html('ایجاد دوستی  <i class="fa fa-plus"></i>').removeClass('red').addClass('green');
            }
            if (t.parents('.follow_box')) {
                t.parents('.follow_box').find('.follower_count strong').text(pn(response.count));
            };
        })
        .fail(function(response) {
            console.log("error");
        })
        .always(function() {
            console.log("complete");
        });

        $('[data-toggle="tooltip"]').tooltip();
        $('.menu-box ul li.parent').attr('data-content', '');
        $('body').on('click', '.menu-box ul li.parent > a', function(event) {
            event.preventDefault();
            p = $(this).parent();
            if (p.attr('collapse') == 'true') {
                p.removeAttr('collapse');
                p.children('ul').slideUp('100');
                p.attr('data-content', "");
            }else{
                p.parent().children('li').removeAttr('collapse');
                p.parent().children('li').children('ul').slideUp('100');
                $(this).parent().attr('collapse', 'true');
                $(this).parent().children('ul').slideDown('100');
                p.attr('data-content', "");

            }
        });
        $('body').on('click', '.menu-box .colse-menu-btn', function(event) {
            event.preventDefault();
            $('.menu-box').width(0);
        });

        $('body').on('click', '.report-btn', function(event) {
            event.preventDefault();
            var t = $(this);
            t.append('<span class="loading-img"></span>');
            $.ajax({
                url: t.attr('href'),
            })
            .done(function(d) {
                if (d.status) {
                    alert_show(d.msg, 'success');
                }else{
                    alert_show(d.msg, 'error');
                }
            })
            .fail(function(d) {
                alert_show('خطا! با مدیریت تماس بگیرید', 'error');
            });
            return false;
        });
        $('body').on('click', '.resp-menu', function(event) {
            event.preventDefault();
            $('.menu-box').css('display', 'block');
            $('.menu-box').animate({
                width: 320},
                100, function() {
                });
        });

        $('body').on('mouseenter', '#wis_navbar > ul > li', function(event) {
            event.preventDefault();
            var t = $(this);
            marker(t);
            var ul = $(this).parent('ul');
            if(t.children('ul').length != 0){
                t.children('ul').stop(true, false).slideDown('fast');
            }
        });
        $('body').on('mouseleave', '#wis_navbar', function(event) {
            $('.marker').css('display', 'none');
        });
        $('body').on('mouseleave', '#wis_navbar > ul > li', function(event) {
            event.preventDefault();
            var t = $(this);
            if(t.children('ul').length != 0){
                t.children('ul').stop(true, false).slideUp(400);
            }
        });

        $('body').on('mouseenter', '.cats > ul > li', function(event) {
            event.preventDefault();
            var t = $(this);
            var ch = t.children('ul.sub-cats');
            $('.sub-cats').slideUp(300);
            if (ch.length > 0) {
                ch.stop(true, true).slideDown(300);
            }
        });
        $('body').on('mouseleave', '.cats > ul > li', function(event) {
            event.preventDefault();
            var t = $(this);
            var ch = t.children('ul.sub-cats');
            if (ch.length > 0) {
                ch.stop(true, true).slideUp(300);
            }
        });

        var l = $('.cats > ul > li');
        l.width(100/l.length+'%');

    });

live_content();
});