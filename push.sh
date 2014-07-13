#!/bin/sh

send(){
	git push origin devel
	ssh wisgoon@direct.wisgoon.com "cd /home2/wisgoon/wisgoon.com/www && git merge devel && touch reload"
}

jsend(){
	git push origin devel
	ssh wisgoon@direct.wisgoon.com "cd /home2/wisgoon/wisgoon.com/www && git merge devel"
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

    jsend)
		git add .
		git commit -m "change on file"
		jsend
        ;;

	*)
		echo "commit\t for autocommit"
		echo "send\t for push and merge"
	;;
esac

