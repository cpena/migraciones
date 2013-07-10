#!/usr/bin/env python
import os
import httplib2
import webapp2
from google.appengine.api import memcache
from apiclient.discovery import build
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from oauth2client.appengine import AppAssertionCredentials 
from google.appengine.ext.webapp import template
import json as simplejson

# BigQuery API Settings
PROJECT_NUMBER = 'XXXXXXXXX' #Your project number

credentials = AppAssertionCredentials(scope='https://www.googleapis.com/auth/bigquery')
http        = credentials.authorize(httplib2.Http(memcache))
service     = build("bigquery", "v2", http=http)

class MigracionesHandler(webapp2.RequestHandler):
	def get(self):
		if self.request.get("q")=="data":
			try:
				max_rows = 100
				if self.request.get("rows"):
					max_rows = self.request.get("rows")
					query     = {'query':'''
									SELECT
										nace_lat,
										nace_lng,
										l.lat AS vive_lat,
										l.lng AS vive_lng,
										count(*) AS cantidad
									FROM
										(SELECT
											l.lat AS nace_lat,
											l.lng AS nace_lng,
											P23B AS vive,
										FROM
											[data-sensing-lab:hoffa.persona] p
										JOIN
											(SELECT location_id,lat,lng FROM [data-sensing-lab:hoffa.location]) l
										 	ON p.P22B = l.location_id
										WHERE 
											p.P22A=2) AS raw
									JOIN
										(SELECT location_id,lat,lng FROM [data-sensing-lab:hoffa.location]) l
										 ON raw.vive = l.location_id
									GROUP BY nace_lat,nace_lng,vive_lat,vive_lng
									ORDER BY cantidad DESC 
									LIMIT
									''' + max_rows,
				             'timeoutMs':30000}
				jobRunner = service.jobs()
				reply     = jobRunner.query(projectId=PROJECT_NUMBER,body=query).execute()
				self.response.out.write(simplejson.dumps(reply,False,False))
			except Exception,e:
				self.response.out.write(simplejson.dumps({'error': '%s'%e},False,False))			
		else:	
			path = os.path.join(os.path.dirname(__file__), 'migraciones.html')
			self.response.out.write(template.render(path,''))

app = webapp2.WSGIApplication([
    ('/', MigracionesHandler)
], debug=True)




