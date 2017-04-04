var express = require('express');
var router = express.Router();

var fs = require('fs');
var readline = require('readline');
var google = require('googleapis');
var googleAuth = require('google-auth-library');
var q = require('q');
var delta = 1;
var slackNoti = 3;
var cancelNoti = 1;
globalNoti = "nothing";
globalAttendees = [];
globalStartTime = "";
globalBookedRoom = "";
globalState = "g";
globalRfid = "";
Array.prototype.diff = function(a) {
    return this.filter(function(i) {return a.indexOf(i) < 0;});
};

var SCOPES = ["https://www.googleapis.com/auth/calendar", "https://www.googleapis.com/auth/admin.directory.resource.calendar"];
var TOKEN_DIR = (process.env.HOME || process.env.HOMEPATH ||
    process.env.UERPROFILE) + '/.credentials/';
var TOKEN_PATH = TOKEN_DIR + 'calendar-nodejs-quickstart.json';

var rooms = {
	"Neptune" : {
		"email": "relaxitaxi.xyz_31353333383835313235@resource.calendar.google.com",
		"id": "1533885125",
		"capacity": "10",
		"occupied": true
	},
	"Saturn" : {
		"email": "relaxitaxi.xyz_3337313539303735353735@resource.calendar.google.com",
		"id": "37159075575",
		"capacity": "5",
		"occupied": false
	}
}

/**
 * Create an OAuth2 client with the given credentials, and then execute the
 * given callback function.
 *
 * @param {Object} credentials The authorization client credentials.
 * @param {function} callback The callback to call with the authorized client.
 */
function authorize(credentials, callback) {

  var clientSecret = credentials.installed.client_secret;
  var clientId = credentials.installed.client_id;
  var redirectUrl = credentials.installed.redirect_uris[0];
  var auth = new googleAuth();
  var oauth2Client = new auth.OAuth2(clientId, clientSecret, redirectUrl);
  delete arguments[0];
  delete arguments[1];
  var result = [];
  for(var i in arguments)
	result.push(arguments[i]);

  var passedArguments = result;
  // Check if we have previously stored a token.
  fs.readFile(TOKEN_PATH, function(err, token) {
    if (err) {
      getNewToken(oauth2Client, callback);
    } else {
      oauth2Client.credentials = JSON.parse(token);
      passedArguments.push(oauth2Client);
      callback.apply(this, passedArguments);
    }
  });
}

/**
 * Get and store new token after prompting for user authorization, and then
 * execute the given callback with the authorized OAuth2 client.
 *
 * @param {google.auth.OAuth2} oauth2Client The OAuth2 client to get token for.
 * @param {getEventsCallback} callback The callback to call with the authorized
 *     client.
 */
function getNewToken(oauth2Client, callback) {
  var authUrl = oauth2Client.generateAuthUrl({
    access_type: 'offline',
    scope: SCOPES
  });
  console.log('Authorize this app by visiting this url: ', authUrl);
  var rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });
  rl.question('Enter the code from that page here: ', function(code) {
    rl.close();
    oauth2Client.getToken(code, function(err, token) {
      if (err) {
        console.log('Error while trying to retrieve access token', err);
        return;
      }
      oauth2Client.credentials = token;
      storeToken(token);
      callback(oauth2Client);
    });
  });
}

/**
 * Store token to disk be used in later program executions.
 *
 * @param {Object} token The token to store to disk.
 */

function storeToken(token) {
  try {
    fs.mkdirSync(TOKEN_DIR);
  } catch (err) {
    if (err.code != 'EEXIST') {
      throw err;
    }
  }
  fs.writeFile(TOKEN_PATH, JSON.stringify(token));
  console.log('Token stored to ' + TOKEN_PATH);
}

function createEvent(organizer, invitees, startTime, endTime, room, auth) {
	var calendar = google.calendar('v3');
	var attendees = [];
	if (invitees.length > 0) {
		invitees = invitees.split(",");

		for (var i = 0; i < invitees.length; i++){
			attendees.push({
				"id": invitees[i],
				"email": invitees[i]
			});
		}
	}

	attendees.push({
		"id": rooms[room]["id"],
		"email": rooms[room]["email"],
		"displayName": room,
		"resource": true
	});

	calendar.events.insert({
		auth: auth,
    	calendarId: 'primary',
    	resource: {
    		"summary": "Smart Office Hackathon Demo",
    		"description": "Smart Office Hackathon Demo",
    		"organizer": {
			    "id": organizer,
			    "email": organizer,
			    "displayName": "Shubham Jindal"
		  	},
		  	"start": {
			    "dateTime": startTime+":00",
			    "timeZone": "Asia/Kolkata"
			},
			"end": {
				"dateTime": endTime+":00",
				"timeZone": "Asia/Kolkata"
			},
			"attendees": attendees
    	}
	}, function(){
		listEvent(auth);
	});
}

var options = {
  host: 'https://www.googleapis.com',
  path: '/admin/directory/v1/customer/my_customer/resources/calendars'
};

function listEvent(auth) {
	var calendar = google.calendar('v3');
	calendar.events.list({
	    auth: auth,
	    calendarId: 'primary',
	    orderBy: 'updated'
	}, function(err, response){
		var events = response.items;
		globalEventId = events[0]["id"];
		calendar.events.get({
        	auth: auth,
        	calendarId: 'primary',
        	eventId: globalEventId
        }, function(err, response) {
        	console.log(response["start"]);
        	globalStartTime = response["start"]["dateTime"];
          globalAttendees = [];
        	var attendees = response["attendees"];

        	for (var j=0; j<attendees.length; j++) {
        		if (attendees[j]["resource"]){
        			globalBookedRoom = attendees[j]["displayName"];
        		}
            else {
              globalAttendees.push(attendees[j]["email"]);
            }
        	}
        });
	});
}

function deleteEvent(globalEventId, auth) {
	var calendar = google.calendar('v3');
	calendar.events.delete({
    	auth: auth,
    	calendarId: 'primary',
    	eventId: globalEventId
    });
}

function listEvents(startTime, endTime, res, auth) {
  var calendar = google.calendar('v3');
  var totalRooms = [];
  for (var k in rooms) totalRooms.push(k);
  var bookedRooms = [];
  var promises = [];
  calendar.events.list({
    auth: auth,
    calendarId: 'primary',
    timeMax: endTime+":00+05:30",
    timeMin: startTime+":00+05:30"
  }, function(err, response) {
    if (err) {
      console.log('The API returned an error: ' + err);
      return;
    }

    var events = response.items;
    if (events.length == 0) {
      console.log('No upcoming events found.');
    } else {
      events.forEach(function(event, eventIdx) {
      	var defer = q.defer();
        var eventId = event["id"];
        calendar.events.get({
        	auth: auth,
        	calendarId: 'primary',
        	eventId: eventId
        }, function(err, response) {
        	var attendees = response["attendees"];
        	for (var j=0; j<attendees.length; j++) {
        		if (attendees[j]["resource"]){
        			defer.resolve(true);
        			bookedRooms.push(attendees[j]["displayName"]);
        		}
        	}
        });
        promises.push(defer.promise);
      });
    }

    q.all(promises).then(function(data){
    	res.send(totalRooms.diff(bookedRooms));
    });
  });
}

/* GET home page. */
router.get('/', function(req, res, next) {

	fs.readFile('client_secret.json', function processClientSecrets(err, content) {
		if (err) {
	    	console.log('Error loading client secret file: ' + err);
	    	return;
		}
		console.log("Hello");
		// Authorize a client with the loaded credentials, then call the
		// Google Calendar API.
		//res.sendStatus(200);
	});
	res.render('index', { title: 'Express' });
});

router.get('/startMeeting', function (req, res, next) {
  var timerId = setTimeout(function(){
    /*var d = new Date();
    var utc = d.getTime() - (d.getTimezoneOffset() * 60000);
    var nd = new Date(utc);

    var ist = new Date(globalStartTime);
    var istDate = new Date(ist.getTime() - (ist.getTimezoneOffset() * 60000));
    var diff = parseInt((nd - istDate)/1000);

    console.log(nd, istDate, diff);
    */
    if (!rooms[globalBookedRoom]["occupied"]) {
      globalNoti = "warn";
    }
  }, slackNoti);
  res.sendStatus(200);
});

router.get('/cancelMeeting', function (req, res, next) {
  var timerId = setTimeout(function(){
    /*var d = new Date();
    var utc = d.getTime() - (d.getTimezoneOffset() * 60000);
    var nd = new Date(utc);

    var ist = new Date(globalStartTime);
    var istDate = new Date(ist.getTime() - (ist.getTimezoneOffset() * 60000));
    var diff = parseInt((nd - istDate)/1000);

    console.log(nd, istDate, diff);*/

    if (!rooms[globalBookedRoom]["occupied"]) {
      
      fs.readFile('client_secret.json', function processClientSecrets(err, content) {
        if (err) {
            console.log('Error loading client secret file: ' + err);
            return;
        }
        // Authorize a client with the loaded credentials, then call the
        // Google Calendar API.
        authorize(JSON.parse(content), deleteEvent, globalEventId);
        globalNoti = "cancel";
        clearInterval(timerId);
        //authorize(JSON.parse(content), listEvent);
        res.sendStatus(200);
      });
    }
  }, cancelNoti);
});

router.get('/capacity', function(req, res, next) {
	var room = req["query"]["room"];
	console.log(rooms[String(room)]["capacity"]);
	res.send(rooms[String(room)]["capacity"]);
});

router.get('/getOccupiedStatus', function(req, res, next) {
	var room = req["query"]["room"];
	res.send(rooms[String(room)]["occupied"]);
});

router.get('/toggleOccupiedStatus', function(req, res, next) {
	var room = req["query"]["room"];
	var status = req["query"]["status"];
	if (status === "1")
		rooms[String(room)]["occupied"] = true;
	else if (status === "0")
		rooms[String(room)]["occupied"] = false;
	res.sendStatus(200);
});

router.post('/bookRoom', function(req, res, next) {
	var organizer = req["body"]["organizer"];
	var invitees = req["body"]["invitees"];
	var startTime = req["body"]["startTime"];
	var endTime = req["body"]["endTime"];
	var room = req["body"]["room"];
	console.log(req["body"]);
	globalStartTime = startTime;
	fs.readFile('client_secret.json', function processClientSecrets(err, content) {
		if (err) {
	    	console.log('Error loading client secret file: ' + err);
	    	return;
		}
		// Authorize a client with the loaded credentials, then call the
		// Google Calendar API.
		authorize(JSON.parse(content), createEvent, organizer, invitees, startTime, endTime, room);
		//authorize(JSON.parse(content), listEvent);
		res.sendStatus(200);
	});
});

router.post('/listAvailableRooms', function(req, res, next) {
	var startTime = req["body"]["startTime"];
	var endTime = req["body"]["endTime"];
	fs.readFile('client_secret.json', function processClientSecrets(err, content) {
		if (err) {
	    	console.log('Error loading client secret file: ' + err);
	    	return;
		}
		// Authorize a client with the loaded credentials, then call the
		// Google Calendar API.
		authorize(JSON.parse(content), listEvents, startTime, endTime, res);
	});
});

router.get('/poll', function(req, res, next){
  var toSend = globalNoti;
  
  if (globalNoti === "warn" || globalNoti === "cancel") {
    globalNoti = "nothing";
  }

  res.send(JSON.stringify({'tosend': toSend, 'attendees': globalAttendees, 'starttime': globalStartTime, 'room': globalBookedRoom}));
});


router.get('/rfid', function(req, res, next) {
  var rfid = req["query"]["rfid"];
  if (rfid.length > 0) {
    globalRfid = rfid;
    if (globalState === "r") {
      globalState = "b";
    }
  }
  res.sendStatus(200);
});

router.get('/car', function(req, res, next) {
  var status = req["query"]["status"];
  if (status === "0") {
    globalState = "g";
    globalRfid = "";
  } else if (status === "1" && globalRfid.length == 0) {
    globalState = "r";
  } else if (status === "1" && globalRfid.length > 0) {
    globalState = "b";
  }
  res.sendStatus(200);
});

router.get('/sety', function(req, res, next) {
  globalState = "y";
  res.sendStatus(200);
});

router.get('/color', function(req, res, next) {
  res.send(globalState);
});

router.get('/getNeptuneStatus', function(req, res, next) {
  res.send(rooms["Neptune"]["occupied"]);
});

module.exports = router;