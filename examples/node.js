var zmq = require('zeromq')
var msgpack = require('msgpack-lite');
var sock = zmq.socket('sub');
sock.connect('tcp://127.0.0.1:49017');
sock.subscribe('');
sock.on('message', function(msg){
    var data = msgpack.decode(msg);
    console.log('Received message:');
    console.log(data);
});
