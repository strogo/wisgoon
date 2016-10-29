#!/bin/sh

send(){
	# git add .
	# git commit -m "changes"
    
    ## git remote add gitlab git@gitlab.com:vchakoshy/wisgoon.git
    git push gitlab master

	git push new devel
	ssh wisgoon@79.127.125.104 "cd /home/wisgoon/new/ && git merge devel && touch reload-new"
}

case $1 in    
    send)
        send
        ;;

    *)
        echo "send\t for push and merge"
    ;;
esac