function alert_show(msg, status) {
    $('body').append('<div class="alert alert_show ' + status + '">' + msg + '</div>');
    setTimeout(function() {
        $('.alert_show').slideUp();
    }, 3000);
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
        isAnimated: false,
        isFitWidth: true,
    });
}

var next_pref = next_pref || '?older='

function load_posts(page) {
    $('.footer-loading-box').show(0);
    // $(".loading").show(0);
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
                // AnetworkAdMatcher("anetwork-xc-banner",_AWFP_user);
            }
        }).done(function(d) {
            $('.footer-loading-box').hide(0);
        })
        .fail(function(d) {
            // alert( "error" );
            $("#next_url").addClass("btn btn-success").html('کلیک کنید');
        })
        .always(function(d) {
            $('.footer-loading-box').hide(0);
        });
    }


// window scroll
$(window).scroll(function() {
    loadingobj = $(".loading");
    var break_point = $(document).height() - ($(window).height() * 2.02);
    if ($(window).scrollTop() >= break_point) {
        var next_page = $('#feed span:last').attr('data-next');
        console.log(next_page);
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
                el.unbind('click').popover({content: d, placement:'bottom',html:true}).popover('show');
                el.parent().children('.loading-img').hide(0);
            })
            .fail(function(d) {
                alert( "error" );
            })
            .always(function(d) {
            });
        }else{
            el.unbind('click').popover({content: notifCache, placement:'bottom',html:true}).popover('show');    
            el.parent().children('.loading-img').hide(0);
        }
    }
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
    .done(function(d) {
        var res = $.parseJSON(d);
        if (res.status == true) {
            alert_show(res.message, 'success');
            t.parents('.comment-item').slideUp('fast');
        }else{
            alert_show('خطا در حذف دیدگاه', 'error');
        }
    })
    .fail(function() {
        alert_show('خطا در حذف دیدگاه', 'error');
    })
    .always(function(d) {
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


$(function () {
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
        var ul = $(this).parent('ul');
        if(t.children('ul').length != 0){
            t.children('ul').stop(true, false).slideDown('fast');
        }
    });
    $('body').on('mouseleave', '#wis_navbar > ul > li', function(event) {
        event.preventDefault();
        var t = $(this);
        if(t.children('ul').length != 0){
            t.children('ul').stop(true, false).slideUp(400);
        }
    });

    $('.cats').children('ul').show();
    var l = $('.cats > ul > li');
    l.width(100/l.length+'%');

})

live_content();

var frm = $("#add-comment-form");
frm.submit(function(e) {
    $('.comment-loading-img').show();
    $("#comment-submit-btn").addClass("disabled");
    e.preventDefault();
    $.ajax({
        type: frm.attr('method'),
        url: frm.attr('action'),
        data: frm.serialize(),
    })
    .done(function(response) {
        if (response == 'error'){
            console.log('Method Not Allowed');
        }else{
            $('#comments_box').prepend(response);
        }
    })
    .fail(function() {
        console.log("error");
    })
    .always(function() {
        $('.comment-loading-img').hide();
        $("#comment-submit-btn").removeClass("disabled");
        $(frm).find("input[type=text], textarea").val("");
        console.log("complete");
    });
    return false;
});