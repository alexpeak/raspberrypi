import http.client, urllib.request, urllib.parse, urllib.error, keys

KEY = keys.key('thingspeak')
#print KEY

def log(stuff,verbose=False):
    stuff['key'] = KEY
    if verbose:
        print(stuff)
    params = urllib.parse.urlencode(stuff)
    headers = {"Content-type": "application/x-www-form-urlencoded","Accept": "text/plain"}
    conn = http.client.HTTPConnection("api.thingspeak.com:80")
    conn.request("POST", "/update", params, headers)
    response = conn.getresponse()
    if verbose:
        print(response.status, response.reason)
    data = response.read()
    conn.close()

#log('field1',20)
