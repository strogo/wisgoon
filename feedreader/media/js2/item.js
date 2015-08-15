var com_offset = 0;
var com_in_act = false;

function load_comments(){
    if (com_in_act == true){
        return;
    }
    com_in_act = true;

    $('#comment_load_more').children('.txt').css('display', 'none');
    $('#comment_load_more').children('.loader').css('display', 'block');
    $.ajax({
        url: comments_url + "?offset=" + com_offset,
    })
    .done(function(d) {
        $('#comment_load_more').children('.txt').css('display', 'block');
        $('#comment_load_more').children('.loader').css('display', 'none');
        if(d == '0'){
            $('#comment_load_more').children('.txt').text('دیدگاه دیگری وجود ندارد');
        }
        else
        {
            $("#comments_box").append(d);
            com_offset += 10;
            com_in_act = false;
        }
    })
    .fail(function(d) {
        console.log("error");
    })
    .always(function(d) {
        $('#comment_load_more').children('.txt').css('display', 'block');
        $('#comment_load_more').children('.loader').css('display', 'none');
    });
}

load_comments();
$("#comment_load_more").click(function(){
    load_comments();
});

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

    feedobj.masonry('reload');
    
});