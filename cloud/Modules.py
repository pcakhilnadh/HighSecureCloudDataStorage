import socket
import uuid
import hashlib
import urllib
import urllib2
from uuid import getnode as get_mac
from datetime import timedelta
from datetime import datetime

from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.http import HttpResponse

from cloud.models import UserProfile,TempStorage,FileDetails,FileShare,Permission,FileAccess,Key,KeyValues


#---------------------------------------------------------------------------------------------------------------------------

def mail(usr):
	toAddress=usr.email 
	name=usr.first_name+" "+usr.last_name
	otp=str(uuid.uuid4())
	timeOut=datetime.now() + timedelta(minutes=15)
	subject=' OTP - Do not Show with Anyone !'
	message="<center><h1> High Secure Cloud Data Storage<h1></center>\n<p>Hello "+name+",\n\n</p>This is your OTP please do not share with anyone.\n\n\n <center><h4>"+otp+"</center></h4>\n\n\n -Thanks,\n<b>HighSecureCloudStorage Team</b>"
	mail=EmailMessage(subject, message, settings.EMAIL_HOST_USER, [toAddress])
	mail.content_subtype = "html"
	#mail.send()

	users = UserProfile.objects.get(user=usr)

	#OTP sms-------------------------------------------------------------------------
	
	username = urllib.quote_plus("weneverdies@gmail.com") 
	hashcode=urllib.quote_plus("cbeb12523f11d3db17fc618179b4db7234aec71f")
	number=urllib.quote_plus("91"+str(users.phone_number))
	sender=urllib.quote_plus("Textlocal")
	message=urllib.quote_plus("HI,"+name+" Your Otp is : "+otp+" Do not share with anyone, Thanks High Secure Cloud Team")
	data='username='+username+'&hash='+hashcode+'&numbers='+number+"&sender="+sender+"&message="+message
	
	#otp details ended--------------------------------------------------------------

	timeDifference=datetime.utcnow()-users.timeout.astimezone(timezone.utc).replace(tzinfo=None) #To subtract offset-naive and offset-aware datetimes
	if timeDifference.total_seconds()>0:
		users.OTP=None
	if users.OTP==None:
		users.timeout=timeOut
		users.OTP=otp
		mail.send()
		response = urllib2.urlopen('https://api.txtlocal.com/send/?'+data)
	
	users.save()
	
#---------------------------------------------------------------------------------------------------------------------------

def login_check(usrname):
	
	mac = get_mac()
	mac = (hex(mac))
	mac =str(mac)
	ValidUser=False
	current_user=User.objects.get(username=usrname)
	users = UserProfile.objects.get(user=current_user)
	if usrname:
		for macAdd in users.MAC.all(): 
			macAdd=str(macAdd)
			if macAdd==mac:
				ValidUser=True

	if ValidUser==True:
		return 1
	else:
		mail(current_user)
		return 0

#---------------------------------------------------------------------------------------------------------------------------
def passwordReset(usrname):
	current_user=User.objects.get(username=usrname)
	users = UserProfile.objects.get(user=current_user)
	toAddress=current_user.email 
	name=current_user.first_name+" "+current_user.last_name
	otp=hashlib.sha224(str(uuid.uuid4())).hexdigest()
	subject=' Password Reset !'
	message="<center><h1> High Secure Cloud Data Storage<h1></center>\n<p>Hello "+name+",\n\n</p>This is your new password please do not share with anyone.\n\n\n <center><h4>"+otp+"</center></h4>\n\n\n -Thanks,\n<b>HighSecureCloudStorage Team</b>"
	mail=EmailMessage(subject, message, settings.EMAIL_HOST_USER, [toAddress])
	mail.content_subtype = "html"
	#mail.send()

	
	#OTP sms-------------------------------------------------------------------------
	"""
	username = urllib.quote_plus("weneverdies@gmail.com") 
	hashcode=urllib.quote_plus("cbeb12523f11d3db17fc618179b4db7234aec71f")
	number=urllib.quote_plus("91"+str(users.phone_number))
	sender=urllib.quote_plus("Textlocal")
	message=urllib.quote_plus("HI,"+name+" Your password has been reseted.Check mail, Thanks High Secure Cloud Team")
	data='username='+username+'&hash='+hashcode+'&numbers='+number+"&sender="+sender+"&message="+message
	#otp details ended--------------------------------------------------------------
	"""
	
		#response = urllib2.urlopen('https://api.txtlocal.com/send/?'+data)
	
	current_user.set_password(otp)
	current_user.save()
	users.save()
	mail.send()
	return True
#---------------------------------------------------------------------------------------------------------------------------

def permissionUpdate(usr,fileid,remove,userList=[]):
	current_user=User.objects.get(username=usr)
	users = UserProfile.objects.get(user=current_user)
	
	fileshare=FileShare.objects.get(file_requested=fileid)
	fileshare.save()
	
	if not userList  :
		permission_temp= fileshare.permission.get(user=users)
		permission_temp.public=0
		permission_temp.save()
		fileshare.save()
	elif "PUBLIC" in userList:
		permission_temp=fileshare.permission.get(user=users)
		permission_temp.public=1
		permission_temp.save()
		fileshare.save()
	else:
		if remove == 1:
			current_user=User.objects.get(username=userList[0])
			user_temp = UserProfile.objects.get(user=current_user)
			permission_temp=fileshare.permission.get(user=user_temp)
			permission_temp.save()
			fileshare.permission.remove(permission_temp)
			fileshare.save()
		else:

			for u in userList:
				current_user=User.objects.get(username=str(u))
				user_temp = UserProfile.objects.get(user=current_user)
				permission_temp=Permission(user=user_temp)
				permission_temp.save()
				fileshare.permission.add(permission_temp)
			fileshare.save()

#---------------------------------------------------------------------------------------------------------------------------
def Arrangement(fileid,keyy,user):
	KEY=[]
	NewKey=[]
	KEY[:0]=keyy
	flag=0
	length=len(keyy)
	filedetails=FileDetails.objects.get(fileId=fileid)
	for i in range (0,length):
		NewKey.append(str(ord(KEY[i])% len(str(user)))) 
		pos=int(ord(KEY[i])%5)
		
		#try:
		#	KeY=Key.objects.get(position=pos)

		#except:
		#	KeY=Key(position=pos)
		KeY=Key(position=pos)
		KeY.save()
		Value=KeyValues(value=KEY[i],RealPosition=i)
		Value.save()
		KeY.keyValues.add(Value)
		KeY.save()
		filedetails.key.add(KeY)
	filedetails.save()

	return ''.join(NewKey)

#----------------------------------------------------------------------------- ----------------------------------------------
def Rearrange(fileid,key):
	

	
	OldKey=[]
	filedetails=FileDetails.objects.get(fileId=fileid)
	i =0
	
		
	for keys in filedetails.key.all():
		for pos in keys.keyValues.all():
			OldKey.append(str(pos))
	
	description= ''.join(OldKey)
	print description
	description=description.split('$#$')[0]
	fileaccess=FileAccess.objects.get(serverUid=description)
	return fileaccess.owner
		    