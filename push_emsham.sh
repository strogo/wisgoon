#!/bin/sh

send(){
	git push origin devel
	ssh emsham@79.127.125.104 "cd /home/emsham/www && git merge devel && touch reload"
}

jsend(){
	git push origin devel
	ssh emsham@79.127.125.104 "cd /home/emsham/www && git merge devel"
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

