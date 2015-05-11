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

// uploader
function createUploader(){            
    var uploader = new qq.FileUploader({
        element: document.getElementById('file-uploader'),
        action: upload_url,
        debug: true,
        multiple: false,
        allowedExtensions : ['png','jpg'],
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
                $('#file-uploader').hide();
                $('.uploaded-image').html('<img src="/media/pin/temp/t/'+responseJSON.file+'">');
                $('#image_field').val(responseJSON.file);
                image_selected=1;
            }else{
                alert('ﺦﻃﺍ ﻪﻧگﺎﻣ ﺬﺧیﺮﻫ ﻑﺍیﻝ.');
            }
        }
    });           
}
createUploader(); 

var parent_to_del = '';

var comment_vote = 1;
$(".comment-up").click(function(){
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


$(".comment-down").click(function(){
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


$( "body" ).on('click', ".delpost", function(){
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
    $.ajax({
        url: like_url,
        success: function(html) {
            ret = html;
            
            var o = jQuery.parseJSON(ret);
            
            obj.html('<i class="glyphicon glyphicon-heart "></i><i>'+o[0].likes+'</i>');
            obj.removeClass('disabled');
            
            if (o[0].user_act == 1){
                obj.children('i').addClass('user-liked');
            }else{
                obj.children('i').removeClass('user-liked');
            }
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
            console.log(d['message']);
        }else{
            th.data('actionid', '1');
            console.log(d['message']);
        }
    })
    .fail(function() {
    })
    .always(function() {
    });
    

});