
#python header files
import os
import time
import urllib2 # for ip
from datetime import timedelta,datetime
from uuid import getnode as get_mac

#django header files
from django.utils import timezone
from django.conf import settings
from django.shortcuts import render_to_response,render
from django.http import HttpResponseRedirect,HttpResponse
from django.template import RequestContext, loader
from django.contrib.auth import authenticate, login ,logout
from django.contrib.auth.models import User 
from django.contrib.auth.decorators import login_required
from django.core.validators import validate_email
from django.core.exceptions import ValidationError,ObjectDoesNotExist
from django.db.models import Q

#app headerfiles
from cloud.models import UserProfile,MacAddress,TempStorage,FileAccess,FileShare,FileDetails,Permission
from cloud.forms import UserForm,UserProfileForm

#user defined header files
from Modules import login_check,permissionUpdate,Arrangement,Rearrange,passwordReset
from GoogleDrive import create_folder,fileUpload,downloadFile,downloadRequestedFile,fileAccessGranted

#---------------------------------------------------------------------------------------------------------------------------

def home(request):
	context = RequestContext(request)
	return render_to_response('index.html',context)

#---------------------------------------------------------------------------------------------------------------------------

def register(request):
    context = RequestContext(request)
    registered = False
    error=0
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)
        password = request.POST['password']
        cpassword = request.POST['cpassword']
        request.POST['username']=request.POST['username'].lower()
        if 'picture' in request.FILES:
            extension = request.FILES['picture'].content_type
            supported_extension=['image/png','image/jpg','image/jpeg']
            if extension not in supported_extension:
                error="Invalid Image Format"
                user_form = UserForm()
                profile_form= UserProfileForm()
                return render_to_response('register.html',{'user_form': user_form, 'profile_form': profile_form, 'registered': registered,'error':error},context)    
            
        if password == cpassword:
            if user_form.is_valid() and profile_form.is_valid():
                user = user_form.save()
                user.set_password(user.password)
                user.save()


                profile = profile_form.save(commit=False)
                profile.user = user
                if 'picture' in request.FILES:
                	request.FILES['picture'].name=user.username
                	profile.picture=request.FILES['picture']
                profile.folder=create_folder(user.username) #create folder in drive with username function defined in GoogleDrive.py
                print request.POST['latitude']+','+request.POST['longitude']
                if request.POST.get('trustedsystem')=='Y':
                    response = urllib2.urlopen('http://maps.googleapis.com/maps/api/geocode/json?latlng='+request.POST['latitude']+','+request.POST['longitude'])
                    r=response.read()
                    mac = get_mac()
                    mac = (hex(mac))
                    MacAdd=MacAddress()
                    MacAdd.address=mac
                    MacAdd.name='My Home '
                    try:
                        MacAdd.route= r.split('short_name')[0].split('long_name')[1].split('"')[2]
                        MacAdd.place=r.split('short_name')[1].split('long_name')[1].split('"')[2]
                        MacAdd.territory=r.split('short_name')[2].split('long_name')[1].split('"')[2]
                        MacAdd.provincial=r.split('short_name')[3].split('long_name')[1].split('"')[2]
                        MacAdd.country=r.split('short_name')[4].split('long_name')[1].split('"')[2]
                        MacAdd.PIN=int(r.split('short_name')[5].split('long_name')[1].split('"')[2])
                    except:
                        pass
                    MacAdd.save()
                    profile.save()
                    profile.MAC.add(MacAdd)
                profile.save()
                registered = True
                
            else:
                error= profile_form.errors
                error=user_form.errors
                
        
        else:
            error="Passwords do not match."
        
    else:
        user_form = UserForm()
        profile_form= UserProfileForm()
    return render_to_response(
            'register.html',
            {'user_form': user_form, 'profile_form': profile_form, 'registered': registered,'error':error},
            context)    

#---------------------------------------------------------------------------------------------------------------------------

def ulogin(request):
    
    context = RequestContext(request)
    error=0
    if request.method == 'POST':
        username = request.POST['username'].lower()
        
        password = request.POST['pwd']
        user = authenticate(username=username, password=password)
        if user==None:
            error= "Invalid login details"
            return render_to_response('login.html', {'error' :error}, context)
            #return HttpResponse("Invalid login details supplied.<a href='/ulogin'>Try Again</a>")
        elif login_check(username)==0 :    # from Modules.py 
            
            error= "Enter OTP sent to your e-mail or mobile number, registered "
            
            return render_to_response('otp.html', {'error' :error,'u':user.id}, context)
        else   :
            if user.is_active:
                login(request,user)
                return HttpResponseRedirect('/')
            else:
                return HttpResponse("Your Account is disabled.")
            
    else:
            
        return render_to_response('login.html', {}, context)

#---------------------------------------------------------------------------------------------------------------------------
def forgot_password(request):
    context = RequestContext(request)
    error=None
    success=None
    if request.method == 'POST':
        try:
            user=User.objects.get(username=request.POST['username'].lower())
            if passwordReset(request.POST['username'].lower()):
                success='Password has been reseted successsfully.Check your email for new password'
        except:
            error="Enter correct username"
    return render_to_response('passwordRecovery.html',{'error' :error,'success' :success},context)

#---------------------------------------------------------------------------------------------------------------------------

def otp(request,user):
    context = RequestContext(request)
    error=False
    current_user = User.objects.get(id=user)
    users=UserProfile.objects.get(user=current_user)
    timeOut=datetime.now() + timedelta(minutes=15)
    timeDifference=datetime.utcnow()-users.timeout.astimezone(timezone.utc).replace(tzinfo=None) #To subtract offset-naive and offset-aware datetimes
    if timeDifference.total_seconds()>0:
        users.OTP=None

    if users.OTP==request.POST['otp']:
        current_user.backend = 'django.contrib.auth.backends.ModelBackend' #Django wanting to make sure you auth the user first. If you want to bypass this you can just use the following before login
        login(request,current_user)
        return HttpResponseRedirect('/')
    else:
        error=True
        return render_to_response('otp.html', {'OTPerror' :error}, context)

#---------------------------------------------------------------------------------------------------------------------------

@login_required
def ulogout(request):
    usr = User.objects.get(username=request.user)
    users = UserProfile.objects.get(user=usr)
    
    users.OTP=None
    users.save()
    logout(request)
    return HttpResponseRedirect('/')

#---------------------------------------------------------------------------------------------------------------------------

@login_required
def profile(request):
    context = RequestContext(request)
    entries = request.user.profile
    #entries = UserProfile.objects.all()
    return render_to_response('profile.html',{'profiles' : entries }, context)

#---------------------------------------------------------------------------------------------------------------------------

@login_required
def setting(request):
    error=None
    success=None    
    context = RequestContext(request)
    current_user = User.objects.get(username=request.user)
    userProfile=UserProfile.objects.get(user=current_user)
    if request.method == 'POST':
        if 'picture' in request.FILES:
            if str(userProfile.picture).split(".")[-2] == ('profile_images/'+str(request.user)):
                os.remove(settings.MEDIA_ROOT+'/'+userProfile.picture.name)

            extension=request.FILES['picture'].name.split(".")[-1]
            request.FILES['picture'].name=str(request.user)+'.'+extension
            userProfile.picture=request.FILES['picture']
            userProfile.save()
            success='Profile Image Updated'

        elif 'currentEmail' in request.POST:
            if current_user.email != request.POST['currentEmail']:
                error='Enter Current Email correctly'
            elif request.POST['newEmail'] != request.POST['reNewEmail']:
                error='New email address missmatch. Type correct email id'
            else:
                try:
                    validate_email( request.POST['newEmail'] )
                    success='Email address successsfully changed to  '+request.POST['newEmail']
                    current_user.email=request.POST['newEmail']
                    current_user.save()
                except ValidationError:
                    error='Enter a proper email ID'            

        elif 'currentPwd' in request.POST:
            if current_user.check_password(request.POST['currentPwd']):
                
                if request.POST['newPwd'] != request.POST['reNewPwd']:
                    error='Password  missmatch. Type password carefully'
                else:
                    current_user.set_password(request.POST['newPwd'] )
                    current_user.save()
                    success='password has been changed successsfully'
                
            else:
                error='Enter Current password correctly'            

        elif 'confirmProfile' in request.POST:
            if 'first_name' in request.POST:
                if current_user.first_name != request.POST['first_name']:  
                    current_user.first_name = request.POST['first_name']
                    current_user.save()
                    success='User Details Updated successsfully '
            if 'last_name' in request.POST:
                if current_user.last_name != request.POST['last_name']:
                    current_user.last_name = request.POST['last_name']
                    current_user.save()
                    success='User Details Updated successsfully '
            if 'gender' in request.POST:
                if userProfile.gender != request.POST['gender']: 
                    userProfile.gender = request.POST['gender']
                    userProfile.save()
                    success='User Details Updated successsfully'
            if 'dob' in request.POST:
                
                if str(userProfile.dob) != str(request.POST['dob']):
                    try:
                        userProfile.dob = request.POST['dob']
                        userProfile.save()
                        success='User Details Updated successsfully '
                    except:
                        error='Invalid Date Format For Date Of Birth'
            if 'phone_number' in request.POST:
                if userProfile.phone_number != request.POST['phone_number']:
                    userProfile.phone_number = request.POST['phone_number']
                    userProfile.save()
                    success='User Details Updated successsfully'
            error='You have not changed any user details.'
        
    return render_to_response('settings.html',{'error':error,'success':success,'profiles' : userProfile,'user':current_user }, context)

#---------------------------------------------------------------------------------------------------------------------------

@login_required(login_url='/ulogin')
def dashboard(request):
    context = RequestContext(request)
    
    NotTrusted=True
    current_user = User.objects.get(username=request.user)
    userProfile=UserProfile.objects.get(user=current_user)
    File=[]
    FileName=[]
    FileID=[]
    FileSize=[]
    permissioN=Permission.objects.all()
    mac = get_mac()
    mac = (hex(mac))
    if current_user.username  in str(permissioN):
            fileShare=FileShare.objects.filter(owner_id=current_user.id)
            
            for f in fileShare:
                File.append(f.file_requested)
    for name in File:
        fileDetails=FileDetails.objects.filter(fileId=name)
        
        for f in fileDetails:
            FileID.append(f.fileId)
            
            FileName.append(str(f.fileName.split('Temp/')[1]))
            FileSize.append(float(format(f.fileSize/1000000.0, '.2f')))
    
    for m in userProfile.MAC.all():
        if m.address==mac:
            NotTrusted=False

    
    filedetails=zip(FileName,FileSize,FileID)
    return render_to_response('dashboard.html',{'quota':userProfile.driveSize,'filedetails':filedetails,'NotTrusted':NotTrusted}, context)

#---------------------------------------------------------------------------------------------------------------------------

@login_required
def dashboardSearch(request):
    context = RequestContext(request)
    
    current_user = User.objects.get(username=request.user)
    userProfile=UserProfile.objects.get(user=current_user)
    File=[]
    FileName=[]
    FileID=[]
    FileSize=[]
    ownership=[]
    permissioN=[]
    
    if 'search' in request.POST and request.POST['search'] != '':
        search_key='Temp/'+request.POST['search']

        filedetails =FileDetails.objects.filter(fileName__startswith=search_key)
        for f in filedetails:
            
            fileshare=FileShare.objects.get( file_requested=f.fileId)
            
            try:
                if fileshare.permission.get(user=current_user):
                    
                    filedet =FileDetails.objects.get(fileId=fileshare.file_requested)
                    ownership.append(fileshare.owner)
                    FileID.append(filedet.fileId)
                    FileName.append(str(filedet.fileName.split('Temp/')[1]))
                    FileSize.append(float(format(filedet.fileSize/1000000.0, '.2f')))
                    filedetails=zip(FileName,FileSize,FileID,ownership)          
                
                
            except ObjectDoesNotExist :
                    try:
                        if fileshare.permission.get(public=1):                    
                            filedet =FileDetails.objects.get(fileId=fileshare.file_requested)
                            ownership.append(fileshare.owner)
                            FileID.append(filedet.fileId)
                            FileName.append(str(filedet.fileName.split('Temp/')[1]))
                            FileSize.append(float(format(filedet.fileSize/1000000.0, '.2f')))
                            filedetails=zip(FileName,FileSize,FileID,ownership)          
                        
                    except ObjectDoesNotExist :
                        filedetails=None

    else:
                
            fileshare=FileShare.objects.all()
            
            for f in fileshare:
                try:
                    if f.permission.get(user=current_user):
                        
                        filedet =FileDetails.objects.get(fileId=f.file_requested)

                        ownership.append(f.owner)
                        FileID.append(filedet.fileId)
                        FileName.append(str(filedet.fileName.split('Temp/')[1]))
                        FileSize.append(float(format(filedet.fileSize/1000000.0, '.2f')))

                        filedetails=zip(FileName,FileSize,FileID,ownership)
                except ObjectDoesNotExist :
                    pass

            filedetails=zip(FileName,FileSize,FileID,ownership)
    return render_to_response('dashboardSearch.html',{'quota':userProfile.driveSize,'filedetails':filedetails}, context)

#---------------------------------------------------------------------------------------------------------------------------

@login_required
def dashboardUpload(request):
    error=None
    success=None
    usr=[]    
    current_user=User.objects.get(username=request.user)
    users = UserProfile.objects.get(user=current_user)
    fileAccess=FileAccess()
    context = RequestContext(request)
    if request.method == 'POST':
        
        try:
            if 'permission' in request.POST:
                if request.POST['permission']=='share':
                    
                    for c in range(1,int(request.POST['count'])+1):
                        try:
                                    user=User.objects.get(username=request.POST[str(c)].strip())
                                    usr.append(str(user))
                        except:
                            error='enter valid username'
                    if str(request.user) in usr:
                        error='you cannot share to  yourself, try only me'
                
                    
                elif request.POST['permission']=='public':
                    usr.append("PUBLIC")
                    
        except:
            error="select a valid permision"
        
        if error==None:
            if 'file' in request.FILES:
                Temp=TempStorage()
                Temp.user=request.user
                Temp.FILE=request.FILES['file']
                size=request.FILES['file'].size
                size/=1000000.0
                size=format(size, '.2f')
                size=float(size)
                users.driveSize+=size
                
                if users.driveSize<100.0: #100 MB max allowed size for a user
                    Temp.save()
                    try:
                        fileAccess.owner=users
                        fileAccess.serverUid=int(round(time.time() * 1000.0))
                        try:

                            fileAccess.ip = urllib2.urlopen('http://ip.42.pl/raw').read()
                            fileAccess.save()
                            key=str(fileAccess.serverUid)+'$#$'+str(fileAccess.ip)
                            if fileUpload(request.user,key,usr):  # from GoogleDrive.py
                                success='File uploaded successsfully'
                                
                            else:
                                error='File couldnot be uploaded Contact HighSeureCloud Team'
                        except:
                            error='Some internal error contact HighSeureCloud Team'
                           
                    except:
                        error='Server error, try again later.'
                else:
                    error='You have exceeded your Quota, contact your CSP'
                instance = TempStorage.objects.all()
                instance.delete()
                os.remove(settings.MEDIA_ROOT+'/Temp/'+str(request.FILES['file']))
        
    return render_to_response('dashboardUpload.html',{'error':error,'success':success}, context)

#---------------------------------------------------------------------------------------------------------------------------

@login_required
def dashboardShare(request):
    error=None
    success=None
    remove=0
    context = RequestContext(request)
    userList=[]
    usr=[]

    if 'permissioN' in request.POST:
        
        fileshare=FileShare.objects.get(file_requested=request.POST['fileid'])


        if request.POST['permissioN']=='share':
            if 'remove' in request.POST:
                if int(request.POST['remove']) == 1:
                    usr.append(str(request.POST['user']))
                    remove=1 
            else:
                    try:
                        for c in range(1,int(request.POST['count'])+1):
                                    user=User.objects.get(username=request.POST[str(c)].strip())
                                    usr.append(str(user))
                    except:
                        error='enter valid username'
                    if str(request.user) in usr:
                        error='you cannot share to  yourself, try only me'
                    
                    for u in usr:
                        current_user=User.objects.get(username=u)
                        user_temp = UserProfile.objects.get(user=current_user)
                        try:
                            if fileshare.permission.get(user=user_temp):

                                error="File already shared with you"
                        except:
                            pass
        elif request.POST['permissioN']=='PUBLIC':
            usr.append("PUBLIC")
        if error==None:
              permissionUpdate(request.user,request.POST['fileid'],remove,usr)     
        
        
    else:
        try:  
            filedetails=FileDetails.objects.get(fileId=request.POST['fileid'])
            fileshare=FileShare.objects.get(file_requested=request.POST['fileid'])
            FileName=str(filedetails.fileName.split('Temp/')[1])
            for permission in fileshare.permission.all():
                        if str(permission) != str(request.user):
                            userList.append(permission)
            
            return render_to_response('dashboardShare.html',{'filename':FileName,'fileshare':fileshare,'userList':userList}, context)
        except:
            error= "File you selected no longer valid. Try Searching again ."
    return render_to_response('dashboardShare.html',{'error':error,'success':success}, context)

#---------------------------------------------------------------------------------------------------------------------------

@login_required
def dashboardIncoming(request):
    context = RequestContext(request)
    current_user = User.objects.get(username=request.user)
    userProfile=UserProfile.objects.get(user=current_user)
    File=[]
    FileName=[]
    FileID=[]
    FileSize=[]
    ownership=[]
    f=FileShare.objects.all().exclude(owner=request.user)
    for fileshare in f:
        try:

            if fileshare.permission.get(user=current_user):
                        
                filedet =FileDetails.objects.get(fileId=fileshare.file_requested)
                ownership.append(fileshare.owner)
                FileID.append(filedet.fileId)
                FileName.append(str(filedet.fileName.split('Temp/')[1]))
                FileSize.append(float(format(filedet.fileSize/1000000.0, '.2f')))

            filedetails=zip(FileName,FileSize,FileID,ownership)          
        except ObjectDoesNotExist :
            pass    
        
    try:
        return render_to_response('dashboardIncoming.html',{'quota':userProfile.driveSize,'filedetails':filedetails}, context)    
    except:
        return render_to_response('dashboardIncoming.html',{}, context)
#---------------------------------------------------------------------------------------------------------------------------
@login_required
def dashboardViewFile(request):
    error=None
    context = RequestContext(request)
    permissioN=[]
    if 'fileid' in request.POST:
        if fileAccessGranted(request.POST['fileid'],request.user):
            filedetails=FileDetails.objects.get(fileId=request.POST['fileid'])
            fileshare=FileShare.objects.get(file_requested=request.POST['fileid'])
            for permission in fileshare.permission.all():
                if str(permission) != str(request.user):
                    permissioN.append(permission)
            FileName=str(filedetails.fileName.split('Temp/')[1])
            FileSize=(float(format(filedetails.fileSize/1000000.0, '.2f')))
        else:
            error=" You dont have permission to view this file "
    else:
        error='You hav not selected a valid file.'
    try:
        return render_to_response('viewFile.html',{'error':error,'filename':FileName,'filesize':FileSize,'fileshare':fileshare,'permission':permissioN}, context)
    except:
        return render_to_response('viewFile.html',{'error':error}, context)
#---------------------------------------------------------------------------------------------------------------------------

@login_required
def download(request):
    
    context = RequestContext(request)
    if 'fileid' in request.POST:
        content=downloadFile(request.POST['fileid'],request.user)
        
        if content:
            print content
            file_name=content
            filez = open('{}'.format(file_name), 'rb')
            response = HttpResponse(filez, content_type='application/pdf')
            response['Content-Disposition'] = "attachment; filename={}".format(file_name)
            os.remove(file_name)
            return response
    else:
        return HttpResponseRedirect('/dashboard/viewFile/')
#---------------------------------------------------------------------------------------------------------------------------
@login_required
def addSystem(request):
    context = RequestContext(request)
    error=None
    MC = get_mac()
    MC = (hex(MC))
    NotTrusted=True        
    macName=[]
    macRoute=[]
    macPlace=[]
    macTerritory=[]
    macProvincial=[]
    macCountry=[]
    macPIN=[]
    macAdd=[]
    userProfile=UserProfile.objects.get(user=request.user)
    for mac in userProfile.MAC.all():
        macName.append(mac.name)
        macRoute.append(mac.route)
        macPlace.append(mac.place)
        macTerritory.append(mac.territory)
        macProvincial.append(mac.provincial)
        macCountry.append(mac.country)
        macPIN.append(mac.PIN)
        macAdd.append(mac.address)
    macdetails=zip(macName,macRoute,macPlace,macTerritory,macProvincial,macCountry,macPIN,macAdd)

    if request.method == 'POST':
        try:
            if request.POST['mac_name'].strip() != '':
                response = urllib2.urlopen('http://maps.googleapis.com/maps/api/geocode/json?latlng='+request.POST['latitude']+','+request.POST['longitude'])
                r=response.read()
                MacAdd=MacAddress()
                MacAdd.address=MC
                MacAdd.name=request.POST['mac_name']
                MacAdd.route= r.split('short_name')[0].split('long_name')[1].split('"')[2]
                MacAdd.place=r.split('short_name')[1].split('long_name')[1].split('"')[2]
                MacAdd.territory=r.split('short_name')[2].split('long_name')[1].split('"')[2]
                MacAdd.provincial=r.split('short_name')[3].split('long_name')[1].split('"')[2]
                MacAdd.country=r.split('short_name')[4].split('long_name')[1].split('"')[2]
                MacAdd.PIN=int(r.split('short_name')[5].split('long_name')[1].split('"')[2])

                MacAdd.save()
                userProfile.save()
                userProfile.MAC.add(MacAdd)
                return HttpResponseRedirect('/addSystem/')
            else:
                error="Problem in Entering Details. Try Again with a valid Name."

        except:
            pass
    
        if 'delete' in request.POST:
            
            userProfile=UserProfile.objects.get(user=request.user)
            MacAdd=userProfile.MAC.get(address=request.POST['macAddress'])

            if MacAdd:
                userProfile.MAC.remove(MacAdd) 
                MacAdd.delete()
            return HttpResponseRedirect('/addSystem/')
    for m in userProfile.MAC.all():
        if m.address==MC:
            
            NotTrusted=False
    return render_to_response('TrustedSystem.html',{'error':error,'macdetails':macdetails,'NotTrusted':NotTrusted}, context)
#---------------------------------------------------------------------------------------------------------------------------