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

COOKIES = {"_grabcad_session":"asd....1se"} #TODO: login at https://grabcad.com/community/login and extract this cookie value

def download(url, out, filename, cookies=COOKIES):
    #print(cookies)
    #resp = session.get(url, stream=True)
    resp = requests.get(url, stream=True, cookies=cookies)
    if resp.status_code == 200:
        with open(out / filename, 'wb') as f:
            for chunk in resp.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)