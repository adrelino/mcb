from scrapper.grab_cad import run
from scrapper.wget_cookie import download
from pathlib import Path

if __name__ == "__main__":
    url = "https://grabcad.com/community/api/v1/models/sma-nut-screw-holder-1/files/download?cadid=a9b9f435fe0ef609fffa20ec9e97bf12"
    p=Path("test")
    p.mkdir(exist_ok=True)
    download(url, p, "ANTENA SCREW002.step")
    #run("nut")