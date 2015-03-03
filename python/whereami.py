import netifaces
import urllib.request, urllib.error, urllib.parse
import json

FREEGEOIP = "http://freegeoip.net/json/"
IF = 'eth0'

def myIP():
    return netifaces.ifaddresses(IF)[netifaces.AF_INET][0]['addr']

def whereAmI():
    return json.loads(urllib.request.urlopen(FREEGEOIP + myIP()).read())

def main():
    print(whereAmI()['city'] + ", " + whereAmI()['country_name'])

if __name__ == '__main__':
  main()
