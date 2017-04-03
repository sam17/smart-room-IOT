var mysql = require('mysql');

var connection = mysql.createConnection({
    host: 'localhost',
    port: 3306,
    user: 'root',
    password: 'singcontroller',
    database: 'hackathon'
});

module.exports = connection;