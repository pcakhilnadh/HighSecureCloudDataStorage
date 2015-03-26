#!/usr/bin/python

import httplib2
import pprint
import pickle
import os

#from apiclient import errors
from apiclient.discovery import build
from apiclient.http import MediaFileUpload
from oauth2client.client import OAuth2WebServerFlow
from django.conf import settings
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect,HttpResponse

from cloud.models import UserProfile,TempStorage,FileDetails,FileShare,Permission,FileAccess

from Modules import Rearrange,Arrangement
#---------------------------------------------------------------------------------------------------------------------------

CLIENT_ID = '527872149361-0j63flf45cl368rrv3i6cn0tc97snkt7.apps.googleusercontent.com'
CLIENT_SECRET = 'd53YUXp6jmzB5rPh82CZRAtq'
OAUTH_SCOPE = 'https://www.googleapis.com/auth/drive'
REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'
# Run through the OAuth flow and retrieve credentials
flow = OAuth2WebServerFlow(CLIENT_ID, CLIENT_SECRET, OAUTH_SCOPE, REDIRECT_URI)
with open('google_acc.pkl', 'rb') as input:
  credentials = pickle.load(input)
# Create an httplib2.Http object and authorize it with our credentials
http = httplib2.Http()
http = credentials.authorize(http)
drive_service = build('drive', 'v2', http=http)

#---------------------------------------------------------------------------------------------------------------------------

def create_folder(folder_name):
  folderName=folder_name  
  body = {
          'title': folderName,
          'mimeType': "application/vnd.google-apps.folder"
        }
  root_folder = drive_service.files().insert(body = body).execute()
  return root_folder['id']

#---------------------------------------------------------------------------------------------------------------------------


def fileUpload(usr,key,userList=[]):
   

  try:
    current_user=User.objects.get(username=usr)
    users = UserProfile.objects.get(user=current_user)
    parent_id=users.folder
    Temp = TempStorage.objects.get(user=current_user)
    size=Temp.FILE.size
    size/=1000000.0
    size=format(size, '.2f')
    size=float(size)
    users.driveSize+=size
    users.save()              
    filename=str(Temp.FILE)
    fil='/'+filename
    types={"xls" :'application/vnd.ms-excel',"xlsx" :'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',"xml" :'text/xml',"ods":'application/vnd.oasis.opendocument.spreadsheet',"csv":'text/plain',"tmpl":'text/plain',"pdf": 'application/pdf',"php":'application/x-httpd-php',"jpg":'image/jpeg',"png":'image/png',"gif":'image/gif',"bmp":'image/bmp',"txt":'text/plain',"doc":'application/msword',"js":'text/js',"swf":'application/x-shockwave-flash',"mp3":'audio/mpeg',"zip":'application/zip',"rar":'application/rar',"tar":'application/tar',"arj":'application/arj',"cab":'application/cab',"html":'text/html',"htm":'text/html'}
    extension=filename.split(".")[-1]
    if extension in types:
      mimeType=types[extension]
    else:
      mimeType='text/plain'
    media_body = MediaFileUpload(settings.MEDIA_ROOT+fil, mimetype=mimeType, resumable=True)
    body = {
      'title': filename,
      'description': key,
      'mimeType': mimeType
      }
    body['parents'] = [{'id': parent_id}]
    file_id = drive_service.files().insert(body=body,media_body=media_body).execute()
    FileDet=FileDetails()
    FileDet.fileId=file_id['id']
    #FileDet.fileId='0'
    FileDet.fileName=filename
    FileDet.fileSize=Temp.FILE.size
    FileDet.save()
    fileShare=FileShare()
    fileShare.owner=users
    fileShare.file_requested=FileDet
    fileShare.save()
    userList.append(users)
    
    perm=[]
    
    if "PUBLIC" in userList:
        permission_temp=Permission(user=userList[1],public=1)
        permission_temp.save()
        fileShare.permission.add(permission_temp)
        fileShare.save()
    else:
      for u in userList:
        current_user=User.objects.get(username=str(u))
        user_temp = UserProfile.objects.get(user=current_user)
        permission_temp=Permission(user=user_temp)
        permission_temp.save()
        fileShare.permission.add(permission_temp)
      fileShare.save()
    key=Arrangement(file_id['id'],key,usr)
    file = drive_service.files().get(fileId=file_id['id']).execute()
    file['description'] = key
    drive_service.files().update(fileId=file_id['id'],body=file).execute()
    
    return True

  except:
    return False

#---------------------------------------------------------------------------------------------------------------------------

def downloadFile(fileid,usr):
  
  try:
    file = drive_service.files().get(fileId=fileid).execute()
    key=file['description']
    owner=Rearrange(fileid,key)

    fileshare=FileShare.objects.get(owner=owner,file_requested=fileid)
    try:   
      if fileshare.permission.get(public=1):
        return downloadRequestedFile(fileid,file)
    except:
      try:
        if fileshare.permission.get(user=usr):
          return downloadRequestedFile(fileid,file)
      except:
        return False
  except:
    return HttpResponseRedirect('/dashboard/viewFile/') 


#---------------------------------------------------------------------------------------------------------------------------

def downloadRequestedFile(file_id,drive_file):
  
  download_url = drive_file.get('downloadUrl')
  print download_url
  if download_url:
    resp, content = drive_service._http.request(download_url)
    if resp.status == 200:
      
      file_name = str(drive_file['title'].split('Temp/')[1])
      """
      path_to_file = "/media/".format(file_name)
      response = HttpResponse(mimetype='application/force-download')
      response['Content-Disposition'] = 'attachment; filename=%s' % smart_str(file_name)
      response['X-Sendfile'] = smart_str(path_to_file)
      #return response
      print file_name
      """
      fo = open(file_name, "wb")
      fo.write(content)
      fo.close()
      return file_name
      
#---------------------------------------------------------------------------------------------------------------------------

def fileAccessGranted(fileid,usr):
  try:  
      file = drive_service.files().get(fileId=fileid).execute()
      key=file['description']

      owner=Rearrange(fileid,key)
      
      fileshare=FileShare.objects.get(file_requested=fileid,owner=owner)
      
      if fileshare.permission.get(user=usr):
        return True
       
    
  except:
    try:
      if fileshare.permission.get(public=1):
        return True
    except:
        return False


#---------------------------------------------------------------------------------------------------------------------------

def File(fileid):
  file = drive_service.files().get(fileId=fileid).execute()
  file['description'] = "new_description"
  drive_service.files().update(fileId=fileid,body=file).execute()

#---------------------------------------------------------------------------------------------------------------------------
