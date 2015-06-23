from datetime import datetime
from django.http import HttpResponseRedirect
from django.contrib.auth import logout

class SessionMonitorMiddleware:
    def process_request(self,request):
        if not request.user.is_authenticated(): return
        #if request.user.is_superuser: return
        
        now = datetime.utcnow()

        if 'lastActivity' in request.session:    
            lastActivity = request.session['lastActivity']
            
            try:
                from DataMining.models import userPreferences
                timeout = userPreferences.objects.get(user=request.user).logoutTimeout
            except:
                timeout = 5*60
                
            if (now - lastActivity).total_seconds() > timeout:
                logout(request)
                return

        request.session['lastActivity'] = now