#!/bin/sh

sleep_f(){
	printf "Waiting for reloading uwsgi"
	for p in {1..20}
	do
		printf "."
		sleep 1
	done
}

send(){
	git push origin stable
	ssh wisgoon@79.127.125.146 "cd /home/wisgoon/www/wisgoon.com/www && git merge stable && touch reload"
	sleep_f

}

jsend(){
	git push origin devel
	ssh wisgoon@79.127.125.146 "cd /home/wisgoon/www/wisgoon.com/www && git merge devel"

	git push eiffel devel
	ssh wisgoon@79.127.125.99 "cd /home/wisgoon/www && git merge devel"

	git push mars devel
	ssh wisgoon@79.127.125.98 "cd /home/wisgoon/www && git merge devel"

	# git push emsham devel
	# ssh emsham@79.127.125.104 "cd /home/emsham/www && git merge devel"
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
		# git add .
		# git commit -m "change on file"
		jsend
        ;;

	*)
		echo "commit\t for autocommit"
		echo "send\t for push and merge"
	;;
esac

