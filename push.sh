#!/bin/sh

send(){
	git push origin vahid
	ssh root@wisgoon.com -p 2200 "cd /var/www/html/ && git merge vahid && /etc/init.d/httpd restart"
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

