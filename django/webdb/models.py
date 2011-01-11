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

from django.db import models

class Record(models.Model):
	avatarkey = models.CharField(max_length=37)
	scriptkey = models.CharField(max_length=127)
	recordkey = models.CharField(max_length=127)
	recordvalue = models.CharField(max_length=1024)
	lastupdate = models.DateTimeField(auto_now=True, auto_now_add=True)

	def __unicode__(self):
		return " / ".join([self.avatarkey, self.scriptkey, self.recordkey])

