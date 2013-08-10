#!/bin/sh

send(){
	git push origin vahid
	ssh wisgoon@wisgoon.com "cd /home/wisgoon/wisgoon.com/www && git merge vahid && touch reload"
}

case $1 in
	
	
	commit)
		git add .
		git commit -m "change on file"
		send
	;;
	
	send)
		send
        ;;

	*)
		echo "commit\t for autocommit"
		echo "send\t for push and merge"
	;;
esac

