$('body').on('click', ".item-to-index", function(){
    var obj = $(this);
    var like_url=obj.attr('href');
    $.ajax({
        url: like_url,
        success: function(data) {
            var o = jQuery.parseJSON(data)[0];

            if (o.status == 1){
                obj.html('<i class="fa fa-times red"></i>');
                obj.attr('href', o.url);
            }else{
                obj.html('<i class="fa fa-check green"></i>');
                obj.attr('href', o.url);
            }
        }
    });
    return false;
});

$( "body" ).on('click', ".postfault", function(){
    if (confirm('این مطلب تخلف محصوب می شود؟')){
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


// $('body').on('click', '.del-comment', function(){
//     event.preventDefault();
//     var obj = $(this);
//     var row_name = "comment_row_" + $(obj).attr("rel");
//     var req_url = obj.attr('href');
//     $.ajax({
//         url: req_url,
//         success: function(html) {
//             ret = html;
//             if (ret==1){
//                 $("#"+row_name).remove();
//             }
//         }
//     });

//     return false;
// });
