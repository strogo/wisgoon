#!/bin/sh

send(){
	git push origin devel
	ssh wisgoon@ns1.wisgoon.com "cd /home/wisgoon/wisgoon.com/www && git merge devel && touch reload"
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

