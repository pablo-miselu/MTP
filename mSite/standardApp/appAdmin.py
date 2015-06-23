from django.contrib.auth.models import User 
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission

def createPerm(app_label,codename):
    ct = ContentType.objects.get_or_create(app_label=app_label)[0]
    Permission.objects.create(codename=codename,name=app_label+'.'+codename,content_type=ct)

def createUser(username,password):
    u = User.objects.create_user(username=username,password=password)

def createUser2(username,password,logoutTimeout=5*60):
    from DataMining.models import userPreferences
    u = User.objects.create_user(username=username,password=password)
    up = userPreferences(user=u,logoutTimeout=logoutTimeout)
    up.save()


def changePwd(username,newPassword):
    u = User.objects.get(username=username)
    u.set_password(newPassword)
    u.save()

def addPerm(username,app_label,codename):
    u = User.objects.get(username=username)
    ct = ContentType.objects.get(app_label=app_label)
    p = Permission.objects.get(codename=codename,content_type=ct)
    u.user_permissions.add(p)
    u.save()
