var casper = require('casper').create();
var target = casper.cli.args[0];
var ua = casper.cli.args[1];
var ignoredResource = casper.cli.args[2];

casper.on('resource.requested', function(requestData, request) {
    var uri = requestData['url'];

    var i1 = uri.indexOf('?');
    var i2 = uri.indexOf(';');
    if (i1>0){
        uri = uri.substr(0,i1+1);
    } 
    if (i2>0){
        uri = uri.substr(0,i2+1);
    } 
    if (uri != ignoredResource) {
        casper.echo(uri);
    }
    else {
        request.abort();
    }
});

casper.start();
casper.userAgent(ua);

// Open page first time to find all resources
casper.thenOpen(target, function() {
    //firstFetch = false;
    //casper.echo('Downoading using UA: ' + ua);
    //this.echo("loaded");
    //this.reload(function() {
    //    this.echo("loaded again");
    //});
});

casper.run();
