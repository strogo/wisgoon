#!/bin/sh

send(){
	git push origin devel
    ssh wisgoon@79.127.125.146 "cd /home/wisgoon/www/wisgoon.com/www/ && git merge devel && touch reload"

    git push neptune devel
    ssh wisgoon@79.127.125.104 "cd /home/wisgoon/www/ && git merge devel && touch reload"
}

case $1 in    
    send)
        send
        ;;

    *)
        echo "send\t for push and merge"
    ;;
esac