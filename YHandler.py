import requests
from requests_oauthlib import OAuth1
from requests import request
from urlparse import parse_qs
import webbrowser
import csv

GET_TOKEN_URL = 'https://api.login.yahoo.com/oauth/v2/get_token'
AUTHORIZATION_URL = 'https://api.login.yahoo.com/oauth/v2/request_auth'
REQUEST_TOKEN_URL = 'https://api.login.yahoo.com/oauth/v2/get_request_token'
CALLBACK_URL = 'oob'

class YHandler(object):

    def __init__(self, authf):
        self.authf = authf
        self.authd = self.get_authvals_csv(self.authf)

    def get_authvals_csv(self, authf):
        vals = {}    #dict of vals to be returned
        with open(authf, 'rb') as f:
            f_iter = csv.DictReader(f)
            vals = f_iter.next()
        return vals

    def write_authvals_csv(self, authd, authf):
        f = open(authf, 'wb')
        fieldnames = tuple(authd.iterkeys())
        headers = dict((n,n) for n in fieldnames)
        f_iter = csv.DictWriter(f, fieldnames=fieldnames)
        f_iter.writerow(headers)
        f_iter.writerow(authd)
        f.close

    def reg_user(self):
        oauth = OAuth1(self.authd['consumer_key'], client_secret=self.authd['consumer_secret'], callback_uri=CALLBACK_URL)
        response = requests.post(url=REQUEST_TOKEN_URL, auth=oauth)
        qs = parse_qs(response.text)
        self.authd['oauth_token']= (qs['oauth_token'][0])
        self.authd['oauth_token_secret'] = (qs['oauth_token_secret'][0])
        
        #now send user to approve app
        print "You will now be directed to a website for authorization.\n\
        Please authorize the app, and then copy and paste the provide PIN below."
        #webbrowser.open("%s?oauth_token=%s" % (AUTHORIZATION_URL, self.authd['oauth_token']))
        print "%s?oauth_token=%s" % (AUTHORIZATION_URL, self.authd['oauth_token'])
        self.authd['oauth_verifier'] = raw_input('Please enter your PIN:')

        #get final auth token
        self.get_login_token()

    def get_login_token(self):
        oauth = OAuth1(client_key=self.authd['consumer_key'], client_secret=self.authd['consumer_secret'], resource_owner_key=self.authd['oauth_token'], resource_owner_secret=self.authd['oauth_token_secret'], verifier=self.authd['oauth_verifier'])
        response = requests.post(url=GET_TOKEN_URL, auth=oauth)
        print self.authd
        qs = parse_qs(response.content)
        print qs
        self.authd.update(map(lambda d: (d[0], (d[1][0])), qs.items()))
        self.write_authvals_csv(self.authd, self.authf)
        return response

    """
    def refresh_token(self):
        oauth_hook = OAuthHook(access_token=self.authd['oauth_token'], access_token_secret=self.authd['oauth_token_secret'], consumer_key=self.authd['consumer_key'], consumer_secret=self.authd['consumer_secret'])
        response = requests.post(GET_TOKEN_URL, {'oauth_session_handle': self.authd['oauth_session_handle']}, hooks={'pre_request': oauth_hook})
        qs = parse_qs(response.content)
        self.authd.update(map(lambda d: (d[0], (d[1][0])), qs.items()))
        self.write_authvals_csv(self.authd, self.authf)
        """

    def call_api(self, url, req_meth='GET', data=None, headers=None):
        #print url
        oauth = OAuth1(client_key=self.authd['consumer_key'], client_secret=self.authd['consumer_secret'], resource_owner_key=self.authd['oauth_token'], resource_owner_secret=self.authd['oauth_token_secret'], signature_type='auth_header')
        #req = requests.Request(method=req_meth, auth=oauth, url=url, data=data, headers=headers)
        #req_oauth_hook = OAuthHook(self.authd['oauth_token'], self.authd['oauth_token_secret'], self.authd['consumer_key'], self.authd['consumer_secret'], header_auth=True)
        client = requests.session()
        return client.request(auth=oauth, method=req_meth, url=url, data=data, headers=headers)

    def api_req(self, querystring, req_meth='GET', data=None, headers=None):
        base_url = 'http://fantasysports.yahooapis.com/fantasy/v2/'
        url = base_url + querystring
        if ('oauth_token' not in self.authd) or ('oauth_token_secret' not in self.authd) or (not (self.authd['oauth_token'] and self.authd['oauth_token_secret'])):
            self.reg_user()
        query = self.call_api(url, req_meth, data=data, headers=headers)
        
        if query.status_code != 200: #We have both authtokens but are being rejected. Assume token expired. This could be a LOT more robust
            print "BAD TOKENS"
            #self.refresh_token()
            #query = self.call_api(url, req_meth, data=data, headers=headers)
        
        return query
