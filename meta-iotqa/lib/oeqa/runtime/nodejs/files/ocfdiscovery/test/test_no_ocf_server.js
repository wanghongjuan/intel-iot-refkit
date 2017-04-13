const http = require('http'),
    assert = require('assert'),
    util = require('util'),
    spawnSync = require('child_process').spawnSync;

var options_t = {
    host: '127.0.0.1',
    port: 8000,
    path: '',
    method: 'GET',
    headers: {
        'Accept': 'text/json'
    }
};

const testCaseTimeout = 20000,
		waitCommandExecution = 5000;

var options_d = Object.assign({}, options_t);
options_d.path = '/api/oic/d';

var options_p = Object.assign({}, options_t);
options_p.path = '/api/oic/p';

var options_res = Object.assign({}, options_t);
options_res.path = '/api/oic/res';

function operatePort(op, io, protocol, addrMode, port) {
	var command = util.format('iptables -%s %s -p %s --%s %s -j ACCEPT', 
								op, io, protocol, addrMode, port)
	var status = spawnSync('/usr/sbin/iptables', []
						.concat('-' + op)
						.concat(io)
						.concat('-p')
		  				.concat(protocol)
		  				.concat('--' + addrMode)
		  				.concat(port)
		  				.concat('-j')
		  				.concat('ACCEPT'), 
						{
							stdio: [ process.stdin, process.stdout, process.stderr ],
							shell: true
						}).status;
	if (status !== 0) {
		console.log('Failed to execute command: %s', command);
	}
}

function operateRestApiServer(op) {
	var command = util.format('systemctl %s iot-rest-api-server', op);
	var status = spawnSync('/bin/systemctl', []
							.concat(op)
							.concat('iot-rest-api-server'),
							{
								stdio: [ process.stdin, process.stdout, process.stderr ],
								shell: true
							}).status;
	if (status !== 0) {
		console.log('Failed to execute command: %s', command);
	}	
}

describe('Discover when there is no OCF server running', function() {
	this.timeout(testCaseTimeout);

	before(function() {
		operateRestApiServer('start');
		operatePort('A', 'INPUT', 'tcp', 'dport', 8000);
		operatePort('A', 'INPUT', 'udp', 'dport', 5683);
		operatePort('A', 'INPUT', 'udp', 'dport', 5684);
	});

	describe('platformfound event should not be triggered', function() {	
		it('no_ocf_platform_found', function(done) {
			setTimeout(function () {
			var req = http.request(options_p, function(res) {
					res.setEncoding('utf8');
					res.on('data', function (data) {
						var platforms = JSON.parse(data);
						assert.ok(Array.isArray(platforms));
						assert.equal(0, platforms.length);
						done();
				});				
			});
			req.end();
			}, waitCommandExecution);
		});
	});

	describe('devicefound event should not be triggered', function() {
		it('no_ocf_device_found', function(done) {
			setTimeout(function() {
				var req = http.request(options_d, function(res) {
						res.setEncoding('utf8');
						res.on('data', function (data) {
							var devices = JSON.parse(data);
							assert.ok(Array.isArray(devices));
							assert.equal(0, devices.length);
							done();
					});			
				});
				req.end();				
			}, waitCommandExecution);
		});
	});

	describe('resourcefound event should not be triggered', function() {
		it('no_ocf_resource_found', function(done) {
			setTimeout(function() {
				var req = http.request(options_res, function(res) {
						res.setEncoding('utf8');
						res.on('data', function (data) {
							var resources = JSON.parse(data);
							assert.ok(Array.isArray(resources));
							assert.equal(0, resources.length);
							done();
					});			
				});
				req.end();
			}, waitCommandExecution);
		});
	});

	after(function() {
		operateRestApiServer('stop');
		operatePort('D', 'INPUT', 'tcp', 'dport', 8000);
		operatePort('D', 'INPUT', 'udp', 'dport', 5683);
		operatePort('D', 'INPUT', 'udp', 'dport', 5684);
	});
});