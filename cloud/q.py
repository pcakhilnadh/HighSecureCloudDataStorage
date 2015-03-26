
def dashboardSearch(request):
    
    current_user = User.objects.get(username=request.user)
    userProfile=UserProfile.objects.get(user=current_user)
    File=[]
    FileName=[]
    FileID=[]
    FileSize=[]
    ownership=[]
    permissioN=Permission.objects.all()
    
    if 'search' in request.POST and request.POST['search'] != '':
        search_key='Temp/'+request.POST['search']
        if current_user.username  in str(permissioN):
                #for user owner files
                
                fileShare=FileShare.objects.filter(owner_id=current_user.id)
                
                for f in fileShare:
                    File.append(f.file_requested)
                    ownership.append(f.owner)
                #for shared files
                fileShare=FileShare.objects.filter(permission=current_user.id)
                
                for f in fileShare:
                    File.append(f.file_requested)
                    ownership.append(f.owner)
        for name in File:
            fileDetails=FileDetails.objects.filter(fileName__startswith=search_key)
            
            for f in fileDetails:
                    
                FileID.append(f.fileId)
                
                FileName.append(str(f.fileName.split('Temp/')[1]))
                FileSize.append(float(format(f.fileSize/1000000.0, '.2f')))
        context = RequestContext(request)
        
        filedetails=zip(FileName,FileSize,FileID,ownership)
    else:
        if current_user.username  in str(permissioN):
                #for user owner files
                fileShare=FileShare.objects.filter(owner_id=current_user.id)
                
                for f in fileShare:
                    File.append(f.file_requested)
                    ownership.append(f.owner)
                #for shared files
                fileShare=FileShare.objects.filter(permission=current_user.id)
                
                for f in fileShare:
                    File.append(f.file_requested)
                    ownership.append(f.owner)
        for name in File:
            fileDetails=FileDetails.objects.filter(fileId=name)
            
            for f in fileDetails:
                FileID.append(f.fileId)
                
                FileName.append(str(f.fileName.split('Temp/')[1]))
                FileSize.append(float(format(f.fileSize/1000000.0, '.2f')))
        context = RequestContext(request)
        
        filedetails=zip(FileName,FileSize,FileID,ownership)
    return render_to_response('dashboardSearch.html',{'quota':userProfile.driveSize,'filedetails':filedetails}, context)

#---------------------------------------------------------------------------------------------------------------------------
