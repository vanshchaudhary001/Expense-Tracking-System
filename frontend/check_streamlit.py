import urllib.request

try:
    resp = urllib.request.urlopen('http://127.0.0.1:8501', timeout=3)
    print('OK', resp.getcode())
except Exception as e:
    print('ERR', e)
