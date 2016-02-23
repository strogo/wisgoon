// pin images
var image_selected=0;

function setDataToField(){
    var c = document.getElementById("uploaded_image").childNodes[0];
    $('#image_field').val(c.toDataURL());
}

function add_filter_box(){
    Caman("#vintage canvas", function(){this.vintage();this.render();});
    Caman("#lomo canvas", function(){this.lomo();this.render();});
    Caman("#clarity canvas", function(){this.clarity();this.render();});
    Caman("#sinCity canvas", function(){this.sinCity();this.render();});
    Caman("#sunrise canvas", function(){this.sunrise();this.render();});
    Caman("#crossProcess canvas", function(){this.crossProcess();this.render();});
    Caman("#orangePeel canvas", function(){this.orangePeel();this.render();});
    Caman("#love canvas", function(){this.love();this.render();});
    Caman("#grungy canvas", function(){this.grungy();this.render();});
    Caman("#jarques canvas", function(){this.jarques();this.render();});
    Caman("#pinhole canvas", function(){this.pinhole();this.render();});
    Caman("#oldBoot canvas", function(){this.oldBoot();this.render();});
    Caman("#glowingSun canvas", function(){this.glowingSun();this.render();});
    Caman("#hazyDays canvas", function(){this.hazyDays();this.render();});
    Caman("#herMajesty canvas", function(){this.herMajesty();this.render();});
    Caman("#nostalgia canvas", function(){this.nostalgia();this.render();});
    Caman("#hemingway canvas", function(){this.hemingway();this.render();});
    Caman("#concentrate canvas", function(){this.concentrate();this.render();});
}


$('body').on('click', '.upload_img_btn', function(event) {
    event.preventDefault();
    $('#image_upload_input').click();
});

$('body').on('change', '#image_upload_input', function(event) {
    event.preventDefault();
    $('.filters #PresetFilters a').removeClass('selected');
    $('#origin_image, #uploaded_image_origin').remove();
    $('.progress').css('display', 'none');
    var canvas = document.getElementById('uploaded_image_canvas');
    if ($('#uploaded_image #uploaded_image_canvas').length == 0) {
        var canvas = document.getElementById('rendered');
    };
    canvas.width = 500;
    canvas.height = 1000;
    var ctx = canvas.getContext('2d');
    var canvas2 = document.createElement('canvas');
    var ctx2 = canvas2.getContext('2d');
    canvas2.width = 100;
    canvas2.height = 200;

    var reader = new FileReader();
    reader.onload = function(event) {
        $('body').append('<img src="'+reader.result+'" id="origin_image" style="display: none;" />')
        img = new Image();
        img.onload = function(){
            var wrh = img.width / img.height;
            var newWidth = canvas.width;
            var newHeight = newWidth / wrh;
            if (newHeight > canvas.height) {
                newHeight = canvas.height;
                newWidth = newHeight * wrh;
            }
            canvas.height = newHeight;
            canvas.width = newWidth;
            ctx.drawImage(img,0,0, newWidth , newHeight);

            $('body').append('<img src="" alt="" id="uploaded_image_origin" style="display:none;" />')
            $('#uploaded_image_origin').attr('src', canvas.toDataURL());
            // canvas.setAttribute('id', 'rendered');
        }
        img.src = reader.result;


        img2 = new Image();
        img2.onload = function(){
            var wrh = img2.width / img2.height;
            var newWidth = canvas2.width;
            var newHeight = newWidth / wrh;
            if (newHeight > canvas2.height) {
                newHeight = canvas2.height;
                newWidth = newHeight * wrh;
            }
            canvas2.height = newHeight;
            canvas2.width = newWidth;
            ctx2.drawImage(img2,0,0, newWidth , newHeight);

            var f = document.getElementsByClassName('filter');

            for (var i = f.length - 1; i >= 0; i--) {
                var c = canvas2.cloneNode(true);
                var cx = c.getContext('2d');
                cx.drawImage(img2,0,0, newWidth , newHeight);
                c.setAttribute('id', '');
                f[i].innerHTML = '';
                f[i].appendChild(c);
            };
            if (newHeight > 100) {
                newHeight = 100;
            };
            $('.filters .nav_btn').css({
                height: newHeight,
                paddingTop: (newHeight - 14) / 2
            });
            add_filter_box();
        }
        img2.src = reader.result;
        $('.filters #PresetFilters a').css('display', 'block');
    }
    reader.readAsDataURL(this.files[0]);

    $('.filters').show();
    $('button[disabled]').removeAttr('disabled');
    $('#image_upload_input').val('');
    
});

$('body').on('click', '.img_reset_btn', function(event) {
    event.preventDefault();
    $('#uploaded_image').html('');
    $('.filters #PresetFilters a').removeClass('selected');
    var b = $('#uploaded_image_origin').clone();
    b.attr('id', 'rendered').appendTo('#uploaded_image').css('display', 'initial');
    Caman("#uploaded_image img", function(){this.render();});
});


$('body').on('click', '#pin_form .sub_btn', function(event) {
    $(this).attr('disabled', 'disabled').text('لطفا صبر کنید...');
    if ($('.filter.selected').length == 0) {
        $('#image_field').val($('#origin_image').attr('src'));
        $('#pin_form').submit();
    }else{
        var f = $('.filter.selected').attr('id');
        console.log('filterd');
        Caman('#origin_image', function(){
            eval('this.'+f+'()');
            this.render(function(){
                var canv = document.getElementById('origin_image');
                $('#image_field').val(canv.toDataURL());
                $('#pin_form').submit();
            });
        });
    }
});

$('body').on('click', '.del-comment', function(){
    var obj = $(this);
    var row_name = "comment_row_" + $(obj).attr("rel");
    var req_url = obj.attr('href');
    $.ajax({
        url: req_url,
        success: function(resp) {
            if (resp.status){
                $("#"+row_name).slideUp('fast');
            }
            alertify.success(resp.message);
        }
    });
    
    return false;
});


$('#pin_form').ajaxForm({
    beforeSend: function() {
        $('.progress').css('display', 'block');
    },
    uploadProgress: function(event, position, total, percentComplete) {
        var percentVal = percentComplete + '%';
    },
    success: function(res) {
        if (res.status === true) {
            window.location.href = res.location;
        }else{
            $('#pin_form .sub_btn').removeAttr('disabled').text('ذخیره');
            alertify.error('خطا. دوباره تلاش کنید!');
        };
    },
    complete: function(msg) {
        // console.log(msg);
    }
}); 

$('body').on('click', '.filters #PresetFilters a', function(event) {
    event.preventDefault();
    var c = $('#uploaded_image_origin').clone().attr('id', 'img_clone');
    c.appendTo('body');

    var t = $(this);
    $('.filters #PresetFilters a').removeClass('selected');
    t.addClass('selected');
    var fn = t.attr('id');
    t.append('<div class="filter_loader"><img src="/media/v2/images/loading-img.gif" alt="" /></div>');
    $('.filter_loader img').css({
        display: 'block',
        marginTop: ($('.filter_loader').height() - 20) / 2 +'px',
        marginRight: ($('.filter_loader').width() - 30) / 2 +'px'
    });

    Caman('#img_clone', function(){
        eval('this.'+fn+'()');
        this.render(function(){
            $('.uploaded-image').children('*').remove();
            $('#img_clone').appendTo('.uploaded-image');
            $('#img_clone').show().attr('id', 'rendered');            
            t.children('.filter_loader').remove();
        });
    });
});

$('body').on('click', '.img_rotate_btn', function(event) {
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
                alertify.success('تصویر با موفقیت حذف شد');
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

$("body").on('click', '.btn_report, .report-btn',function(){
    if (confirm('آیا این مطلب غیر اخلاقی است و می خواهید گزارش کنید؟')){
        var obj = $(this);
        obj.addClass('disabled');
        var u=obj.attr('href');
        $.ajax({
            url: u,
            success: function(resp) {
                if (resp.status){
                    alertify.success(resp.message);                    
                }else{
                    alertify.error(resp.message);
                }
                $('body').click();                
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