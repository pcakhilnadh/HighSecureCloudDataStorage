#!/usr/bin/python

import httplib2
import pprint
import pickle

from apiclient.discovery import build
from apiclient.http import MediaFileUpload
from oauth2client.client import OAuth2WebServerFlow


# Copy your credentials from the console
CLIENT_ID = '527872149361-0j63flf45cl368rrv3i6cn0tc97snkt7.apps.googleusercontent.com'
CLIENT_SECRET = 'd53YUXp6jmzB5rPh82CZRAtq'

# Check https://developers.google.com/drive/scopes for all available scopes
OAUTH_SCOPE = 'https://www.googleapis.com/auth/drive'

# Redirect URI for installed apps
REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'

# Path to the file to upload
FILENAME = 'document.txt'
USER='akhilnadhpc'
# Run through the OAuth flow and retrieve credentials
flow = OAuth2WebServerFlow(CLIENT_ID, CLIENT_SECRET, OAUTH_SCOPE, REDIRECT_URI)
#comment next two lines after first successfull run
#authorize_url = flow.step1_get_authorize_url()
#print 'Go to the following link in your browser: ' + authorize_url
#code = raw_input('Enter verification code: ').strip()
#uncomment next two lines for second run onwards.
with open('company_data.pkl', 'rb') as input:
    credentials = pickle.load(input)
#comment following line after first run
#credentials = flow.step2_exchange(code)
#comment two lines after successfull first run
#with open('company_data.pkl', 'wb') as output:
 #   pickle.dump(credentials, output, pickle.HIGHEST_PROTOCOL)

# Create an httplib2.Http object and authorize it with our credentials
http = httplib2.Http()
http = credentials.authorize(http)

drive_service = build('drive', 'v2', http=http)

# Insert a file
#media_body = MediaFileUpload(FILENAME, mimetype='text/plain', resumable=True)
#body = {
#  'title': FILENAME,
#  'description': 'A test document',
#  'mimeType': 'text/plain'
#}

#file = drive_service.files().insert(body=body, media_body=media_body).execute()

#pprint.pprint(file)

#insert folder
folderName=USER
body = {
          'title': folderName,
          'mimeType': "application/vnd.google-apps.folder"
        }
root_folder = drive_service.files().insert(body = body).execute()
print root_folder['id']
parent_id= root_folder['id']
#inserting into that file

media_body = MediaFileUpload(FILENAME, mimetype='text/plain', resumable=True)
body = {
    'title': FILENAME,
    'description': 'A test document',
    'mimeType': 'text/plain'
}
  # Set the parent folder.
if parent_id:
	body['parents'] = [{'id': parent_id}]

file = drive_service.files().insert(
	body=body,
	media_body=media_body).execute()

    # Uncomment the following line to print the File ID
    # print 'File ID: %s' % file['id']

