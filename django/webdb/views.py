# Copyright (C) 2010,2011 Nick 'zoni' Groenen <zoni@zoni.nl>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
import settings

from webdb.models import Record

def index(request, scriptkey="", recordkey=""):
	response = HttpResponse(mimetype='text/plain')
	try:
		avatarkey = request.META['HTTP_X_SECONDLIFE_OWNER_KEY']
	except KeyError:
		response.status_code = 400
		response.write("400 Bad Request\nMissing header: X-SecondLife-Owner-Key")
		return response

	if request.method == "GET":
		try:
			r = Record.objects.get(avatarkey=avatarkey, scriptkey=scriptkey, recordkey=recordkey)
			response.write(r.recordvalue)
		except Record.DoesNotExist:
			response.status_code = 404
			response.write("404 Not Found")
	elif request.method == "PUT":
		try:
			r = Record.objects.get(avatarkey=avatarkey, scriptkey=scriptkey, recordkey=recordkey)
		except Record.DoesNotExist:
			r = Record(avatarkey=avatarkey, scriptkey=scriptkey, recordkey=recordkey)
			response.status_code = 201
		r.recordvalue = request.raw_post_data
		r.save()
		response.write(request.raw_post_data)
	elif request.method == "DELETE":
		try:
			r = Record.objects.get(avatarkey=avatarkey, scriptkey=scriptkey, recordkey=recordkey)
			r.delete()
		except Record.DoesNotExist:
			pass
	else:
		response.status_code = 405
		response['Allow'] = "GET PUT DELETE"
		response.write("405 Method Not Allowed\nAllowed methods: GET, PUT, DELETE")
	return response

