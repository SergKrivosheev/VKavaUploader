import requests
from pprint import pprint
from tqdm import tqdm
import json
import time

class VKavaUploader:
    url_vk = 'https://api.vk.com/method/'
    url_ya = 'https://cloud-api.yandex.net/v1/disk/resources/'
    def __init__(self, VKTOKEN, YATOKEN):
        self.params = {
            'access_token': VKTOKEN,
            'v': '5.131'
        }
        self.yatoken = YATOKEN

    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': 'OAuth {}'.format(self.yatoken)
        }

    def _get_upload_link(self, file_path):
        upload_url = self.url_ya + "upload"
        headers = self.get_headers()
        params = {"path": file_path, "overwrite": "true"}
        response = requests.get(upload_url, headers=headers, params=params)
        pprint(response.json())
        return response.json()

    def photos_ava_get(self):
        photos_ava_get_url = self.url_vk + 'photos.get'
        photos_ava_get_params = {
            'owner_id': '33258642',
            'album_id': 'profile',
            'extended': 1
        }
        req = requests.get(photos_ava_get_url, params={**self.params, **photos_ava_get_params}).json()
        dict_photos = {}
        for item in tqdm(req['response']['items']):
            dict_photos[item['likes']['count']] = ''
            for item_ in item['sizes']:
                if item_['type'] == 'z' or item_['type'] == 'w' or item_['type'] == 'y' or item_['type'] == 'x': #т.к. у меня всего одна аватарка с размером z поэтому я выбираю просто все большие
                    dict_photos[item['likes']['count']] = [item_['url'], item_['type']]
                    break
            time.sleep(0.33)
        return dict_photos #возвращаем как результат словарь с key - количество лайков, value - 1 ссылка, 2 размер

    def photos_upload(self):
        photos = self.photos_ava_get()
        counter = 0
        for item in tqdm(photos):
            if counter < 5:
                r = requests.get(photos[item][0])
                href = self._get_upload_link(file_path=f'netology/{item}.jpg').get("href", "")
                response = requests.put(href, data=r.content)
                response.raise_for_status()
                if response.status_code == 201:
                    print("Success")
                time.sleep(0.33)
                counter += 1
            else:
                break
        self.json_upload(photos) #выполняем загрузку json файлов, как аргумент используем словарь

    def json_upload(self, dictionary):
        dict_with_info = dictionary
        counter = 0
        for item in tqdm(dict_with_info):
            if counter < 5:
                json_file = [{"file name": f"{item}.jpg", "size": f"{dict_with_info[item][1]}"}]
                with open(f'{item}.json', 'w') as outfile:
                    json.dump(json_file, outfile)
                href = self._get_upload_link(file_path=f'netology/{item}.json').get("href", "")
                response = requests.put(href, data=open(f'{item}.json', 'rb'))
                response.raise_for_status()
                if response.status_code == 201:
                    print("Success")
                counter += 1
            else:
                break

if __name__ == '__main__':

    with open('YaToken.txt', 'r') as f:
        YATOKEN = f.read()

    with open('VKToken.txt', 'r') as f:
        VKTOKEN = f.read()

    client = VKavaUploader(VKTOKEN, YATOKEN)
    client.photos_upload()