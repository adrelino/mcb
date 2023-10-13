import logging
import os
import shutil
from os.path import join

import requests
import wget
from tqdm import tqdm

from database import agent
from config import grabcad_path
from scrapper.base import filter_escape_char, unzip_file, move_file, convert_to_obj, get_keyword_id
from utils.utils import make_dir, clean_dir
from tools import create_image
from pathlib import Path
from scrapper.wget_cookie import download

grapcad_url = 'https://grabcad.com'
api_url = f'{grapcad_url}/community/api/v1/models'
login_url = f'{grapcad_url}/login'
sw_ext_mapping = {
    'stl': '.stl',
    'obj': '.obj',
    'ptc-creo-parametric': '.prt',
    'solidworks': '.sldprt',
}


def search(keyword, softwares, page=1, per_page=100, sort='following', time='all_time'):
    payload = {
        'page': str(page),
        'per_page': str(per_page),
        'query': keyword,
        'softwares': softwares,
        'sort': sort,
        'time': time,
    }
    r = requests.post(api_url, data=payload)
    if r.status_code == 200:
        models = []
        images = []
        for item in r.json()['models']:
            models.append(item['cached_slug'])
            images.append(item['preview_image'])
        return models, images, r.json()['total_entries']
    else:
        raise ConnectionError


def get_models(keyword, softwares=None):
    if softwares is None:
        softwares = ["obj"]
    per_page = 100
    model_names, images, total_models = search(keyword, per_page=per_page, softwares=softwares)
    #insert_search_log(keyword, total_models, softwares)
    for i in tqdm(range(total_models // per_page)):
        model_name, image, _ = search(keyword, page=i + 2, softwares=softwares)
        model_names += model_name
        images += image
    print(f'{total_models} models found.')
    return model_names, images


def get_archive_url(cached_slug):
    url = f'{api_url}/{cached_slug}'
    r = requests.get(url)
    if r.status_code == 200:
        if 'archive_url' in r.json():
            archive = r.json()['archive_url']
            if archive == None:
                return None
            else:
                return archive#.split('=')[-1]
        else:
            return None
    else:
        raise ConnectionError

def get_files(cached_slug):
    url = f'{api_url}/{cached_slug}/files'
    r = requests.get(url)
    if r.status_code == 200:
        obj = r.json()
        if 'files' in obj:
            return obj['files']
        else:
            return None
    else:
        raise ConnectionError

def download_files(files):
    p = Path("downloadDir")
    p.mkdir(exist_ok=True)
    for file in files:
        url = file["download_url"]
        name = file["name"]
        print(url, name)
        download(url, p, name)
    return p

def download_zipfile(cadid, output_dir):
    url = f'https://d2t1xqejof9utc.cloudfront.net/cads/files/{cadid}/original.zip'
    return wget.download(url, out=output_dir)


def filter_files(keyword, unzipped_dir, softwares):
    formats = [sw_ext_mapping[software] for software in softwares]
    files = []
    for file in os.listdir(unzipped_dir):
        filename, ext = os.path.splitext(file)
        if (ext.lower() in formats) and (keyword in filename.lower()):
            files.append(file)

    return files


def insert_search_log(keyword, total, sws):
    return agent.insert('search_log',
                        **{
                            'keyword': keyword,
                            'etc': f"softwares : {';'.join(sws)}",
                            'website': 'grabCAD',
                            'total': total
                        })


def insert_grabcad_file(cadid, filepath, model_name, image, keyword_id):
    if not os.path.isfile(filepath):
        raise FileNotFoundError

    filepath = filter_escape_char(filepath)
    payload = {
        'name': model_name,
        'source_id': cadid,
        'file': filepath,
        'web_image': image,
        'source': 3,
        'image': filepath.replace('/grabCAD/', '/image/grabCAD/').replace('.obj', '.png'),
        'label': keyword_id,
        'file_size': os.path.getsize(filepath)

    }
    return agent.insert('cad_file', ignore=True, **payload)


def is_model(cadid):
    return not agent.read(f"SELECT * from cad_file WHERE source = 3 and source_id='{cadid}'").empty


def run(keyword, softwares=None):
    keyword = keyword.lower()
    if softwares is None:
        softwares = ['obj']

    output_dir = f'{grabcad_path}/{keyword}'
    make_dir(output_dir)
    keyword_id = 1#get_keyword_id(keyword)

    # search models
    model_names, model_images = get_models(keyword, softwares=softwares)

    for model_name, model_image in tqdm(zip(model_names, model_images)):
        try:
            model_name = filter_escape_char(model_name)

            # filter by model name
            if keyword not in model_name.lower():
                continue

            # check model validity
            # cadid = get_cadid(model_name)
            # print(model_name, cadid)
            # if not cadid:
            #     continue

            #arch = get_archive_url(model_name)
            #print(model_name, arch)

            # check db
            #if is_model(cadid):
            #    continue

            # unzip model
            # zip_file = download_zipfile(cadid, output_dir)
            # unzipped_dir = unzip_file(zip_file)

            files = get_files(model_name)
            unzipped_dir = download_files(files)

            # extract files with valid extension
            files = filter_files(keyword, unzipped_dir, softwares)
            if not files:
                shutil.rmtree(unzipped_dir)
                continue

            # move valid files
            for file in files:
                moved_file = move_file(join(unzipped_dir, file), output_dir)
                obj_file = convert_to_obj(moved_file)
                insert_grabcad_file(cadid, obj_file, model_name, model_image, keyword_id)

            # remove unzipped directory
            shutil.rmtree(unzipped_dir)

        except Exception as e:
            logging.error(f'[{keyword}]:{e}')

    clean_dir(output_dir)
    create_image(output_dir)