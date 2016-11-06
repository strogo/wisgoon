var com_offset = 0;
var com_in_act = false;

function load_comments(){
    var l = $('#comment_load_more');
    if (com_in_act == true){
        return;
    }
    com_in_act = true;

    l.find('.txt').css('display', 'none');
    l.parent().find('span').hide();
    l.find('.loader').css('display', 'block');

    $.ajax({
        url: comments_url + "?offset=" + com_offset,
    })
    .done(function(d) {
        if(d == '0'){
            l.find('.txt').css('display', 'block');
            l.parent().find('span').css('display', 'none');
            l.find('.txt').text('دیدگاه دیگری وجود ندارد');
        }
        else
        {
            l.parent().find('span').show();
            $("#comments_box").append(d);
            com_offset += 10;
            com_in_act = false;
        }
    })
    .fail(function(d) {
        console.log("error");
    })
    .always(function(d) {
        l.find('.loader').css('display', 'none');
        l.find('.txt').css('display', 'block');
        cmnt_loaded = true;
    });
}

load_comments();
$("#comment_load_more").click(function(){
    load_comments();
});

$(function () {
    $.ajax({
        url: related_url
    }).
    done(function(d){
        var feedobj = $('#feed');
        $(feedobj).html(d);

        feedobj.masonry({
            itemSelector : '.feed-item',
            isRTL: true,
            isAnimated: false,
            isFitWidth: true,
        });
        ms_reload();
        // feedobj.masonry('reload');
    });



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
        .done(function(res) {
            if (res.status == 'false'){
                alertify.error(res.message);
            }else{
                var cnt_comment;
                $('#comments_box').prepend($.parseHTML(res.message));
                $('#comments_box').find('.no-comment').hide('fast');
                cnt_comment = document.getElementById('cnt_comment');
                cnt_comment.innerHTML=pn(res.cnt_comments + 1);
                alertify.success("دیدگاه شما با موفقیت ثبت شد");
            }
        })
        .fail(function() {
            alertify.error("خطا! با مدیریت سایت تماس بگیرید");
        })
        .always(function() {
            $('.comment-loading-img').hide();
            $("#comment-submit-btn").removeClass("disabled");
            $(frm).find("input[type=text], textarea").val("");
        });
        return false;
    });
});
