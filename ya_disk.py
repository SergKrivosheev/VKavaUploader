import requests
from tqdm import tqdm
import json
import time
from pprint import pprint


class YaUploader:
    YAURL = 'https://cloud-api.yandex.net/v1/disk/resources/'

    def __init__(self, YATOKEN):
        self.yatoken = YATOKEN

    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': 'OAuth {}'.format(self.yatoken)
        }

    def get_upload_link(self, file_path):
        upload_url = self.YAURL + "upload"
        headers = self.get_headers()
        params = {"path": file_path, "overwrite": "true"}
        response = requests.get(upload_url, headers=headers, params=params)
        pprint(response.json())
        return response.json()

    def upload_json(self, dictionary, file_path):
        json_file = []
        for item in tqdm(dictionary):
            dict_elem = {"file name": f"{item}.jpg",
                         "size": f"{dictionary[item][1]}"}
            json_file.append(dict_elem)
        with open(f'info.json', 'w') as outfile:
            json.dump(json_file, outfile)
        href = self.get_upload_link(
                        file_path=f'{file_path}/info.json').get("href", "")
        response = requests.put(href, data=open(f'info.json', 'rb'))
        response.raise_for_status()
        if response.status_code == 201:
            print("Success")

    def upload_photos(self, dictionary, file_path):
        self.create_directory(file_path)
        for item in tqdm(dictionary):
            r = requests.get(dictionary[item][0])
            href = self.get_upload_link(
                        file_path=f'{file_path}/{item}.jpg').get("href", "")
            response = requests.put(href, data=r.content)
            response.raise_for_status()
            if response.status_code == 201:
                print("Success")
                time.sleep(1)
        self.upload_json(dictionary, file_path)

    def create_directory(self, path):
        requests.put(f'{self.YAURL}?path={path}', headers=self.get_headers())