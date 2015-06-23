from django.http import HttpResponse , HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import permission_required, login_required
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.models import User
from django.template import RequestContext

import json

from appForms import LoginForm


def render(name,template,data,request):
    from django.template import RequestContext
    from django.shortcuts import render_to_response


    from siteConfig.settings import DEBUG
    import os
    templatePath = os.path.join(name.split(".")[-2]+'_templates',template)
    data['DEBUG'] = DEBUG
    return render_to_response(templatePath,data,context_instance=RequestContext(request))



permissionTupleList = [
    ('_write','A user of '),
]



@login_required(login_url=reverse_lazy('standardApp.views_login.loginView'))
def permissionDenied(request):
    return render(__name__,'permissionDenied.html',{},request)

def loginView(request):
    nextUrl = '/'    
    msg = ''
    if request.method == 'POST':
        nextUrl = request.POST['next']
    
        form = LoginForm(request.POST)
        print form.is_valid()
        if form.is_valid() and auth(request)['status'] == 'sucess':
            return HttpResponseRedirect(nextUrl)
        else:
            msg = 'Incorrect username or password'
    else:
        if 'next' in request.GET:
            nextUrl = request.GET['next']
        form = LoginForm()
    
    return render(__name__,'login.html',
                  {'form': form,'next':nextUrl,'msg':msg},
                  request)

def auth(request):
    response = {}
    response['status'] = 'default'
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)

    if user is not None:
        if user.is_active:
            login(request, user)
            response['status'] = 'sucess'
        else:
            response['status'] = 'disabledUser'
    else:
        response['status'] = 'badUserPasswordCombo'
    return response


@login_required(login_url=reverse_lazy('standardApp.views_login.loginView'))
def logout_view(request):
    logout(request)
    return render(__name__,'logout.html',{},request)
