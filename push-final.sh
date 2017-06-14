#!/bin/sh

send(){
    git push gitlab master
	git push origin devel
    ssh wisgoon@79.127.125.104 "cd /home/wisgoon/www/ && git merge devel && touch reload"
}

jsend(){
	git push origin devel
    ssh wisgoon@79.127.125.104 "cd /home/wisgoon/www/ && git merge devel"
}

case $1 in
    send)
        send
        ;;

    jsend)
		jsend
		;;

    *)
        echo "send\t for push and merge"
    ;;
esac
