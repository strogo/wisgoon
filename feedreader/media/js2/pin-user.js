// pin images
var image_selected=0;
$("#pin_form").submit(function(){
    if(image_selected == 0){
        alert('لطفا یک تصویر انتخاب کنید');
        return false;
        
    }else{
        return true;
    }
});

function setDataToField(){
    var c = document.getElementById("uploaded-image").childNodes[0];
    $('#image_field').val(c.toDataURL());
}

function add_filter_box(){
    Caman("#vintage img", function(){this.vintage();this.render();});
    Caman("#lomo img", function(){this.lomo();this.render();});
    Caman("#clarity img", function(){this.clarity();this.render();});
    Caman("#sinCity img", function(){this.sinCity();this.render();});
    Caman("#sunrise img", function(){this.sunrise();this.render();});
    Caman("#crossProcess img", function(){this.crossProcess();this.render();});
    Caman("#orangePeel img", function(){this.orangePeel();this.render();});
    Caman("#love img", function(){this.love();this.render();});
    Caman("#grungy img", function(){this.grungy();this.render();});
    Caman("#jarques img", function(){this.jarques();this.render();});
    Caman("#pinhole img", function(){this.pinhole();this.render();});
    Caman("#oldBoot img", function(){this.oldBoot();this.render();});
    Caman("#glowingSun img", function(){this.glowingSun();this.render();});
    Caman("#hazyDays img", function(){this.hazyDays();this.render();});
    Caman("#herMajesty img", function(){this.herMajesty();this.render();});
    Caman("#nostalgia img", function(){this.nostalgia();this.render();});
    Caman("#hemingway img", function(){this.hemingway();this.render();});
    Caman("#concentrate img", function(){this.concentrate();this.render();});
}

// uploader
function createUploader(){
    var uploader = new qq.FileUploader({
        element: document.getElementById('file-uploader'),
        action: upload_url,
        debug: false,
        multiple: false,
        allowedExtensions : ['png','jpg','jpe', 'jpeg', 'gif'],
        sizeLimit : 1024*1024*10,
        messages : {
          'typeError':'{file} برای بارگذاری مناسب نیست. تنها {extensions} فرمت ها مجاز هستند.',
          'sizeError':'{file} بسیار حجیم است. فایل شما باید کمتر از {sizeLimit} باشد.',
          'minSizeError':'{file} بسیار کوچک است. فایل شما باید بیشتر از {minSizeLimit} باشد.',
          'emptyError':'{file} فایل خالی است!',
          'onLeave':'فایل در حال بارگذاری است. در صورت ترک صفحه این عملیات لغو می شود.'},
          showMessage:function(message){ 
            alert(message); 
        },
        onComplete : function(id, fileName, responseJSON){
            if(responseJSON.success)
            {
                $('.uploaded-image').html('<img id="img_thumb" src="'+responseJSON.file_o+'">');
                $('#origin_image').remove();
                Caman('#img_thumb', function(){
                    this.render(function(){
                        setDataToField();
                    });
                });

                $('body').append('<img src="'+responseJSON.file_o+'" id="origin_image" style="display:none;" />');
                $('.filters').show();
                $('.qq-upload-size').hide('fast');
                // $('#image_field').val(responseJSON.file_o);
                image_selected=1;

                $('.filters #PresetFilters a').css('display', 'block').html('<img src="'+responseJSON.file_t+'" />');

                add_filter_box();



            }else{
                alert('ﺦﻃﺍ ﻪﻧگﺎﻣ ﺬﺧیﺮﻫ ﻑﺍیﻝ.');
            }
        }
    });           
}
createUploader(); 

$('body').on('click', '.filters #PresetFilters a', function(event) {
    event.preventDefault();
    var c = $('#origin_image').clone().attr('id', 'img_clone');
    c.appendTo('body');

    var t = $(this);
    var fn = t.attr('id');
    t.append('<div class="filter_loader"><img src="/media/v2/images/loading-img.gif" alt="" /></div>');

    Caman('#img_clone', function(){
        eval('this.'+fn+'()');
        this.render(function(){
            $('.uploaded-image').children('*').remove();
            $('#img_clone').appendTo('.uploaded-image');
            $('#img_clone').show().attr('id', 'rendered');            
            t.children('.filter_loader').remove();
            setDataToField();
        });
    });
});

var angleInDegrees=0;

$('body').on('click', '.img_rotate_btn', function(event) {
    var canvas = document.getElementById("img_thumb");
    if (typeof canvas == 'undefined' || canvas == null) {
        var canvas = document.getElementById("rendered");
    }

    angleInDegrees+=90;

    var image=document.createElement("img");
    // image.onload=function(){
    //     drawRotated(canvas, image, 0);
    // }
    // image.src=$('#origin_image').attr('src');
    image.src = canvas.toDataURL();

    angleInDegrees= angleInDegrees % 360;
    drawRotated(canvas, image, angleInDegrees);
});

function drawRotated(canvas, image, degrees){
    // canvas = document.createElement("canvas");
    var ctx=canvas.getContext("2d");
    var w = canvas.width;
    var h = canvas.height;

    if(degrees == 90 || degrees == 270) {
        canvas.width = image.height;
        canvas.height = image.width;
    } else {
        canvas.width = image.width;
        canvas.height = image.height;
    }

    ctx.clearRect(0,0,canvas.width,canvas.height);
    if(degrees == 90 || degrees == 270) {
        ctx.translate(image.height/2,image.width/2);
    } else {
        ctx.translate(image.width/2,image.height/2);
    }
    ctx.rotate(degrees*Math.PI/180);
    ctx.drawImage(image,-image.width/2,-image.height/2);
    document.getElementById('uploaded-image').innerHTML = '';

    document.getElementById('uploaded-image').appendChild(canvas);
}

var parent_to_del = '';

var comment_vote = 1;
$('body').on('click', '.comment-up', function(event) {
    event.preventDefault();
    if (comment_vote == 0){
        return false;
    }
    comment_vote = 0
    comment_id = $(this).attr('rel');
    url = "/pin/comment/score/"+comment_id+'/1'
    $.ajax({
        url: url,
        success: function(html) {
            $("#comment_vote_cnt_"+comment_id).html(html);
            comment_vote = 1;
        }
    });
});


$('body').on('click', '.comment-down', function(event) {
    if (comment_vote == 0){
        return false;
    }
    comment_vote = 0
    comment_id = $(this).attr('rel');
    url = "/pin/comment/score/"+comment_id+'/0'
    $.ajax({
        url: url,
        success: function(html) {
            $("#comment_vote_cnt_"+comment_id).html(html);
            comment_vote = 1;
        }
    });
});


$("body").on('click', ".delpost", function(){
    if (confirm('این مطلب حذف شود؟')){
        var obj = $(this); 
        var parent_to_del = $(obj).parents("div.feed-item");
        
        obj.addClass('disabled');
        var like_url=obj.attr('href');
        $.ajax({
            url: like_url,
            success: function(html) {
                ret = html;
                if (ret==1){
                    $(parent_to_del).remove();
                    feedobj.masonry('reload');
                }
            }
        });
    }
    return false;
});
$( "body" ).on('click', ".noppost", function(){
    var obj = $(this); 
    var parent_to_del = $(obj).parents("div.feed-item");
    
    obj.addClass('disabled');
    var like_url=obj.attr('href');
    $.ajax({
        url: like_url,
        success: function(html) {
            ret = html;
            if (ret==1){
                $(parent_to_del).remove();
                feedobj.masonry('reload');
            }
        }
    });
    return false;
});

$("body").on('click', '.btn_report',function(){
    if (confirm('آیا این مطلب غیر اخلاقی است و می خواهید گزارش کنید؟')){
        var obj = $(this);
        obj.addClass('disabled');
        var like_url=obj.attr('href');
        $.ajax({
            url: like_url,
            success: function(html) {
                var res = jQuery.parseJSON(html);
                obj.removeClass('disabled');
                if (res[0].status){
                    obj.addClass('btn-danger');
                }
                
                alert(res[0].msg);
            }
        });
    }
    return false;
});

$('body').on('click', '.btn_like',function(){
    var obj = $(this);
    obj.addClass('disabled');
    var like_url=obj.attr('href');
    var n = parseInt(en(obj.children('span.count').text()));
    if (obj.parents('.post_item_inner').length > 0) {
        if (obj.parent().hasClass('user-liked')) {
            $('.post_item_inner').find('a.btn_like').parent().removeClass('user-liked');
            $('.liker_avatars').find('.my_avatar').remove();
            $('.post_item_inner').find('a.btn_like').children('span.count').text(pn(n - 1));
        }else{
            $('.post_item_inner').find('a.btn_like').parent().addClass('user-liked');
            $('.liker_avatars').prepend('<a href="'+profile_url+'" class="my_avatar"><img src="'+profile_avatar+'" /></a>');
            $('.post_item_inner').find('a.btn_like').children('span.count').text(pn(n + 1));
        }
    }else{
        if (obj.parent().hasClass('user-liked')) {
            obj.parent().removeClass('user-liked');
            obj.children('span.count').text(pn(n - 1));
        }else{
            obj.parent().addClass('user-liked');
            obj.children('span.count').text(pn(n + 1));
        }        
    }

    $.ajax({
        url: like_url,
        success: function(html) {
            ret = html;
            var o = jQuery.parseJSON(ret);
            obj.removeClass('disabled');
            // if (obj.parents('.post_item_inner').length > 0) {
            //     if (o[0].user_act == 1){
            //         $('.post_item_inner').find('a.btn_like').parent().addClass('user-liked');
            //         $('.liker_avatars').prepend('<a href="'+profile_url+'" class="my_avatar"><img src="'+profile_avatar+'" /></a>');
            //         alert_show('با موفقیت لایک شد', 'success');
            //     }else{
            //         $('.post_item_inner').find('a.btn_like').parent().removeClass('user-liked');
            //         $('.liker_avatars').find('.my_avatar').remove();
            //         alert_show('لایک شما با موفقیت حذف شد', 'success');
            //     }
            //     $('.post_item_inner').find('a.btn_like').children('span.count').text(pn(o[0].likes));
            // }else{                
            //     if (o[0].user_act == 1){
            //         obj.parent().addClass('user-liked');
            //         alert_show('با موفقیت لایک شد', 'success');
            //     }else{
            //         obj.parent().removeClass('user-liked');
            //         alert_show('لایک شما با موفقیت حذف شد', 'success');
            //     }
            //     obj.children('span.count').text(pn(o[0].likes));
            // }
        },
        error: function(){
            alertify.error('مشکلی پیش آمده است. با مدیریت تماس بگیرید');
        }
    });
return false;
});

$('body').on('click', '.topuser-hover-btn',function(){
    var th = $(this);
    var userid = th.data('userid');
    var actionid = th.data('actionid');
    var url = '/pin/follow/'+userid+'/'+actionid+'/';

    $.ajax({
        url: url,
    })
    .done(function(data) {
        var d = $.parseJSON(data);
        if (d['status'] == true) {
            th.data('actionid', '0');
        }else{
            th.data('actionid', '1');
        }
    })
    .fail(function() {
    })
    .always(function() {
    });
});

$('body').on('click', '.block_btn', function(event) {
    event.preventDefault();
    var t = $(this);
    if (t.hasClass('unblock')) {
        var action = 'unblock';
        t.children('span').text('بلاک کاربر');
        t.children('i').removeClass('fa-user').addClass('fa-ban');
        t.removeClass('unblock');
        alertify.success('با موفقیت رفع بلاک شد');
    }else{
        var action = 'block';
        t.children('span').text('رفع بلاک');
        t.children('i').removeClass('fa-ban').addClass('fa-user');
        t.addClass('unblock');
        alertify.success('کاربر با موفقیت بلاک شد');
    }
    
    $.ajax({
        url: t.attr('href'),
        data: {action: action},
    })
    .fail(function(d) {
        alertify.error('خطا در بلاک کردن. با مدیریت تماس بگیرید');
    });
    return false;
    
});

$('#fromImageModal, #fromUrlModal').on('show.bs.modal', function (e) {
    $('.nav .menu-box').hide('fast');
});

$('body').on('click', '.reply-comment', function(event) {
    event.preventDefault();
    var t = $(this);
    $('#id_comment').val($('#id_comment').val() + ' @' + t.data('user'));
    $('#id_comment').focus();
});

$('body').on('click', '.modal_buttons.actions li', function(event) {
    event.preventDefault();
    var t = $(this);
    $('.modal_buttons.actions li').removeClass('active');
    t.addClass('active');
});