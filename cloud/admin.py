from django.contrib import admin
from cloud.models import UserProfile,TempStorage,FileDetails,FileShare,Permission,FileAccess,Key,KeyValues,MacAddress

admin.site.register(UserProfile)
admin.site.register(FileShare)
admin.site.register(FileDetails)
admin.site.register(TempStorage)
admin.site.register(FileAccess)
admin.site.register(MacAddress)
admin.site.register(KeyValues)
admin.site.register(Key)


