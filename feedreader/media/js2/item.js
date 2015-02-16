var com_offset = 0;
var com_in_act = false;

function load_comments(){
    if (com_in_act == true){
        return;
    }
    com_in_act = true;
    $.get(
        comments_url + "?offset=" + com_offset,
        function(response) {
            $("#comments_box").append(response);
            com_offset += 10;
            com_in_act = false;
        }
    );
}

load_comments();
$("#comment_load_more").click(function(){
    load_comments();
});