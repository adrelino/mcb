# login based on https://gist.github.com/tetafro/7e1eb8549c324835cf23a283d9e60aed, but currently not used
# login has to be done in browser so far and then cookie extracted

import requests

# BASE_URL = 'https://grabcad.com/community'
# AUTH_URL = BASE_URL + '/login'
# CREDENTIALS = {"format":"json",
#     "member":{
#         "email":"foo@gmail.com",
#         "password":"c.....j",
#         "authenticity_token":"asdf....+/2YCw=="
#     }
# }
# session = requests.Session()
# session.post(AUTH_URL, data=CREDENTIALS)
# print(session.cookies)

def get_auth_cookie(url):
    cookies = {}
    if url.startswith("https://grabcad.com"):  #TODO login at https://grabcad.com/login and then go to https://grabcad.com/dashboard and extract "_grabcad_session" cookie value e.g. from "dashboard" XHR request
        cookies = {"_grabcad_session" : "asd....1se"}
    elif url.startswith("https://3dwarehouse.sketchup.com"):   #TODO login and go to https://3dwarehouse.sketchup.com/my_3d_warehouse and extract "SID" cookie value e.g. from "me" XHR request
        cookies = {"SID" : '"AuthKey 123....569"'}
    return cookies

def download(url, out, filename):
    #resp = session.get(url, stream=True)
    cookies = get_auth_cookie(url)
    resp = requests.get(url, stream=True, cookies=cookies)
    if resp.status_code == 200:
        with open(out / filename, 'wb') as f:
            for chunk in resp.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
            print(resp.status_code, url, "saved to:", out/filename)
    else:
        print(resp.status_code, url, "cookies:", cookies)