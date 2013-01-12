var fs = require('fs');                                                                        
var io = require('socket.io').listen(1312);

var soc;

console.log("Watching change.txt, listening at 1312");

fs.watchFile('change.txt', function(curr,prev) {
        console.log("current mtime: " +curr.mtime);
        console.log("previous mtime: "+prev.mtime);
        if (curr.mtime.getTime() == prev.mtime.getTime()) {
            console.log("mtime equal");
        } else {
            console.log("mtime not equal");
            io.sockets.emit('data',"hello");
            console.log('change on file and emit hello!');

        }   
});
