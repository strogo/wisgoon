$('body').on('click', ".item-to-index", function(){
    var obj = $(this);
    var like_url=obj.attr('href');
    $.ajax({
        url: like_url,
        success: function(data) {                
            var o = jQuery.parseJSON(data)[0];
            
            if (o.status == 1){
                obj.html('<i class="icon-remove-sign"></i>');
                obj.attr('href', o.url);
            }else{
                obj.html('<i class="icon-ok-sign"></i>');
                obj.attr('href', o.url);
            }
        }
    });
    return false;
});