import urllib
import urllib2
import cookielib
from BeautifulSoup import BeautifulSoup

# stdlib imports
#import logging
import json

from localVars import openid_url, openid_test_user

#Fields = parse_submit(request)
cj = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
urllib2.install_opener(opener)
#url = settings.AUTH_OPENID_URLS['signin']
url = openid_url

open_url = urllib2.urlopen(url)
html = open_url.read()

doc = BeautifulSoup(html)
csrf_input = doc.find(attrs = dict(name = 'csrfmiddlewaretoken'))
csrf_token = csrf_input['value']


#params = urllib.urlencode(dict(username=fields.get("username"), password=fields.get("password"),csrfmiddlewaretoken=csrf_token))

params = urllib.urlencode(dict(username=openid_test_user["username"], password=openid_test_user["password"],csrfmiddlewaretoken=csrf_token))


print params
# This is a blocking call for some crazy unknown reason.  TODO FIX
post_url = urllib2.urlopen(url, params)

print post_url

openid_user = json.loads(post_url.read())

print openid_user



# test seems successfull, next is to persist the user_id in the session ..