import requests
from scrapper.wget_cookie import download
from pathlib import Path

from scrapper.dw import run

url = 'https://3dwarehouse.sketchup.com/warehouse/v1.0/entities'

def search(keyword, per_search=100, offset=0):
    payload = {
        'count': per_search,
        'recordEvent': 'false',
        'q': keyword,
        'fq': 'attribute:categories:domain:string=="Industrial";binaryNames=exists=true',
        'showBinaryMetadata': 'true',
        'showAttributes': 'false',
        'showBinaryAttributes': 'true',
        'offset': offset,
        'contentType': '3dw',
    }

    r = requests.get(url, params=payload)

    if r.status_code == 200:
        js = r.json()
        print(js)
        return js
    else:
        raise ConnectionError

if __name__ == "__main__":
    #search("nut") #no login needed for this part
    #run("nut")
    url = 'https://3dwarehouse.sketchup.com/warehouse/v1.0/entities/3d2c1f19-adc7-4ff3-813f-f4f93a44ee34/binaries/zip?download=true'
    p=Path("test")
    p.mkdir(exist_ok=True)
    download(url, p, "M10_NUT.zip")
