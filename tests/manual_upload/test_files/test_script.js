'use strict';

var express = require('express');
var app = express();

var bodyParser = require('body-parser');
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }))


app.post('/post/', function(req, res) {
   // print to console
   console.log(JSON.stringify(req.body));

   // just call res.end(), or show as string on web
   res.send(JSON.stringify(req.body, null, 4));
});

console.log('It listens on port "7002"');
app.listen(7002);