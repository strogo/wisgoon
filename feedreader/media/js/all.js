var feedobj = $('#feed-ul');
var loadingobj ;
var a_url = a_url || "";
var extend_query = extend_query || "";
var disable_masonry = disable_masonry || 0 ;

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
    $.get(
        a_url + next_pref + page + '&'+extend_query,
        function(response) {
            if(response==0){
                loadingobj.hide();
            }else{
                var $boxes = $(response);
                feedobj.append( $boxes ).masonry( 'appended', $boxes );
                feedobj.masonry('reload');
                loadingobj.hide();
                start_loading=0;
                ana_ajax(a_url + next_pref + page + '&'+extend_query);
            }
        }
    );
}


// window scroll
$(window).scroll(function() {
    loadingobj = $(".loading");
    var break_point = $(document).height() - ($(window).height() * 2.02);
    if ($(window).scrollTop() >= break_point) {
        var next_page = $('#feed-ul span:last').attr('data-next');
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
$("#ScrollToTop").click(function(){
	$('html, body').animate({scrollTop: $("#wrapper").offset().top}, 1000);
});


$(".popnotify").bind('click',function(){
    var el=$(this);
    if (isVisible){
        $(el).popover('hide');
    }else{
        isVisible = true;
        if(!notifCache){
            $.get(el.attr('data-load'),function(d){
                notifCache=d;
                el.unbind('click').popover({content: d, placement:'bottom',html:true}).popover('show');
            });
        }else{
            el.unbind('click').popover({content: notifCache, placement:'bottom',html:true}).popover('show');    
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



live_content();