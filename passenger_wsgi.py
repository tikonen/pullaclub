import sys, os
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(),"pullaclub"))
os.environ['DJANGO_SETTINGS_MODULE'] = "pullaclub.settings"
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
