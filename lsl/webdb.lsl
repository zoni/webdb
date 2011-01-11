// Copyright (C) 2010 Nick 'zoni' Groenen <zoni@zoni.nl>
// 
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
// 
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.

// {{{ API notes

// Link num -445 used for webdb->slave communication
// str format = type|scriptkey|recordkey|status where type is one of GET,PUT,DELETE
// id format = value
//
// Link num -446 used for slave->webdb communication
// str format = type|scriptkey|recordkey where type is one of GET,PUT,DELETE
// id format = value

//}}}

// {{{ Global variables / Constants

string WEBDB_URL = "https://zoni.nl/lsl/webdb/";
list _httpCue = []; // Strided list, stride format [http key, webdb request type, scriptkey, recordkey, value]
integer _cueActive = FALSE; // Timer running
integer _httpErrors = 0;

// }}}

// {{{ Function definitions

// Enable cue if not yet active
enableCue() {
	if(!_cueActive) {
		_cueActive = TRUE;
		webdb_cue_schedulecheck();
	}
}

// Add a request to cue
webdb_cue_add(string type, string scriptkey, string recordkey, string value) {
	if(type != "GET" && type != "PUT" && type != "DELETE") {
		llSay(DEBUG_CHANNEL, "Type error: Webdb only supports modes GET, PUT, DELETE");
	} else {
		_httpCue += [NULL_KEY, type, scriptkey, recordkey, value];
		enableCue();
	}
}

// Schedule the next cue check
webdb_cue_schedulecheck() {
	float delay = 0.85 - llGetTime();
	if(delay <= 0.0) {
		webdb_cue_check();
	} else {
		llSetTimerEvent(delay);
	}
}

// Execute pending requests and stop cue timer when none pending
webdb_cue_check() {
	integer len = llGetListLength(_httpCue);
	integer i = 0;
	while(i<len) {
		key request = llList2Key(_httpCue, i);
		if(request == NULL_KEY) { 
			// Null key, meaning request pending
			webdb_execute(i);
			// In case the http_response ever gets lost, this will make sure the cue
			// is checked again in the future
			llSetTimerEvent(300.0);
			return;
		}
		i += 5; // Next request key is 4 items further in list
	}
	// No requests pending, disable timer
	_cueActive = FALSE;
	llSetTimerEvent(0.0);
}

// Execute a pending request
webdb_execute(integer index) {
	string method = llList2String(_httpCue, index+1);
	string scriptkey = llList2String(_httpCue, index+2);
	string recordkey = llList2String(_httpCue, index+3);
	string value = llList2String(_httpCue, index+4);
	
	key request = llHTTPRequest(llDumpList2String([WEBDB_URL, scriptkey, "/", recordkey], ""), [HTTP_METHOD, method], value);
	llResetTime();
	_httpCue = llListReplaceList(_httpCue, [request], index, index); 
}

// }}}

// {{{ Default state
default {
	http_response(key request_id, integer status, list metadata, string body) {
		integer index = llListFindList(_httpCue, [request_id]); // Check if request originates from this script
		if(index != -1) {
			// Normal http response codes
			if(llListFindList([200, 201, 404], [status]) != -1) { 
				string type = llList2String(_httpCue, index+1);
				string scriptkey = llList2String(_httpCue, index+2);
				string recordkey = llList2String(_httpCue, index+3);
				string value = body;

				if(_httpErrors > 0) {
					llOwnerSay("webdb connection re-established");
					_httpErrors = 0;
					_cueActive = TRUE;
				}

				llMessageLinked(LINK_SET, -445, llDumpList2String([type, scriptkey, recordkey, status], "|"), value);
				// Request handled, remove from cue
				_httpCue = llDeleteSubList(_httpCue, index, index+4);

			// Http responses indicating likely temporary errors (network timeout,
			// dns lookup failure, etc) which may be tried again
			} else if(llListFindList([0, 499, 500, 503, 504], [status]) != -1) { 
				// Reset request key to have it picked up from the cue again
				// on the next cue tick
				_httpCue = llListReplaceList(_httpCue, [NULL_KEY], index, index);

				// Report error
				llSay(DEBUG_CHANNEL, llDumpList2String(["HTTP Error", status], " "));
				_httpErrors++;
				if(_httpErrors > 10) {
					// Don't let it go past 10, to limit max retry rate to 
					// once every 10 minutes in case of continued failures
					_httpErrors = 10;
				} else if(_httpErrors <= 1) { 
					// Only give feedback on the first error
					llOwnerSay("webdb connection lost");
				}
				// Back off from making new requests for a bit
				llSetTimerEvent((float) (_httpErrors*60));
				_cueActive = TRUE;
				return;
			} else if(status == 301) {
				// In case of the configured instance of webdb moving,
				// 301 is expected to be returned for all requests, along with
				// some helpful feedback to the user.
				// In that case, display body, sleep for a while and then reset
				// to avoid further requests being made (And the user being spammed)
				llOwnerSay(body);
				llSleep(3600.0);
				llResetScript();
			} else {
			// Http responses indicating unusual errors, unlikely to be temporary, 
			// requests for these should not be repeated
				if(_httpErrors > 0) {
					llOwnerSay("webdb connection re-established");
					_httpErrors = 0;
					_cueActive = TRUE;
				}

				// Request handled, remove from cue
				_httpCue = llDeleteSubList(_httpCue, index, index+4);
			}
			webdb_cue_schedulecheck();
		}
	}

	link_message(integer link_num, integer num, string str, key id) {
		if(num == -446) {
			list parsed = llParseStringKeepNulls(str, ["|"], []);
			string method = llList2String(parsed, 0);
			string scriptkey = llList2String(parsed, 1);
			string recordkey = llList2String(parsed, 2);
			string value = (string) id;

			webdb_cue_add(method, scriptkey, recordkey, value);
		}	
	}

	timer() {
		webdb_cue_check();
	}
}
// }}}

