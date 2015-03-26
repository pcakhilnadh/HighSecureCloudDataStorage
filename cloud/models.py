from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator,MaxValueValidator, MinValueValidator

from datetime import datetime
import ast


#-------------------------------------------------------------------------------------------

class MacAddress(models.Model):
    address = models.CharField(max_length = 20,null=True,blank=True)
    name = models.CharField(max_length = 50,null=True,blank=True,default='home')
    route = models.CharField(max_length = 50,null=True,blank=True,default='home')
    place = models.CharField(max_length = 50,null=True,blank=True,default='home')
    territory = models.CharField(max_length = 50,null=True,blank=True,default='home')
    provincial = models.CharField(max_length = 50,null=True,blank=True,default='home')
    country = models.CharField(max_length = 50,null=True,blank=True,default='home')
    PIN = models.IntegerField(max_length = 10,null=True,blank=True)
    def __unicode__(self):
    	return self.address
#-------------------------------------------------------------------------------------------

class UserProfile(models.Model):
    user = models.OneToOneField(User,primary_key=True)
    GENDER_CHOICES = (('Male', 'M'),('Female', 'F'))
    picture = models.ImageField(upload_to='profile_images', blank=True,default='profile_images/new_user.png')
    timeout = models.DateTimeField(blank=True, null=True,default=datetime.now())
    OTP=models.CharField(max_length = 100,blank=True,null=True)
    gender = models.CharField(max_length=8, choices=GENDER_CHOICES)
    dob = models.DateField(default=datetime.now())
    folder=models.CharField(max_length = 100,blank=True)
    phone_number = models.CharField(max_length=15, blank=True) 
    MAC=models.ManyToManyField(MacAddress,related_name='macAddress')
    driveSize=models.FloatField(validators = [MinValueValidator(0.0), MaxValueValidator(100)],default=0)
    def __unicode__(self):
    	return self.user.username
    User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])

#-------------------------------------------------------------------------------------------

class KeyValues(models.Model):
    value=models.CharField(max_length=1,blank=True)
    RealPosition=models.IntegerField(max_length=1,blank=True)
    def __unicode__(self):
        return str(self.value)

#-------------------------------------------------------------------------------------------

class Key(models.Model):
    position=models.IntegerField(max_length=1,blank=True)
    keyValues=models.ManyToManyField(KeyValues)
    def __unicode__(self):
        return str(self.position)

#-------------------------------------------------------------------------------------------

class FileDetails(models.Model):
    fileId = models.CharField(max_length = 100,primary_key=True,db_index=True)
    fileName=models.CharField(max_length = 100)
    fileSize=models.IntegerField(max_length = 1000,blank=True,default=0)
    key=models.ManyToManyField(Key)
    def __unicode__(self):
        return self.fileId

#-------------------------------------------------------------------------------------------

class TempStorage(models.Model):
    user = models.OneToOneField(User,primary_key=True)
    FILE=models.FileField(upload_to='Temp')

    def __unicode__(self):
        return self.FILE

#-------------------------------------------------------------------------------------------

class FileAccess(models.Model):
    owner = models.ForeignKey(UserProfile)
    ip=models.IPAddressField()
    serverUid=models.CharField(max_length = 100)
    
    def __unicode__(self):
        return '%s ' % (self.serverUid)

#-------------------------------------------------------------------------------------------

class Permission(models.Model):

    user = models.ForeignKey(UserProfile)
    public=models.IntegerField(max_length=1,default=0)
    def __unicode__(self):
        return str(self.user)

#-------------------------------------------------------------------------------------------

class FileShare(models.Model):
    owner = models.ForeignKey(UserProfile)
    file_requested=models.ForeignKey(FileDetails)
    permission=models.ManyToManyField(Permission)
    
    def __unicode__(self):
        return str(self.owner)

#-------------------------------------------------------------------------------------------
