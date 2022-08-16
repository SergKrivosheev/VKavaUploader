import requests
from tqdm import tqdm
import json
import time
import configparser
from pprint import pprint


class VKDownloader:
    VKURL = 'https://api.vk.com/method/'

    def __init__(self, VKTOKEN):
        self.params = {
            'access_token': VKTOKEN,
            'v': '5.131'
        }

    def get_user_id(self, id):
        get_user_id_url = self.VKURL + 'users.get'
        get_user_id_params = {
            'user_ids': id
        }
        req = requests.get(get_user_id_url,
                           params={**self.params, **get_user_id_params}).json()
        for item in req["response"]:
            user_id = item['id']
        time.sleep(1)
        return user_id

    def get_photos(self, id, photos_quantity):
        get_photos_url = self.VKURL + 'photos.get'
        if id.isdigit():
            user_id = id
        else:
            user_id = self.get_user_id(id)
        get_photos_params = {
            'owner_id': user_id,
            'album_id': 'profile',
            'extended': 1,
            'count': photos_quantity
        }
        req = requests.get(get_photos_url,
                           params={**self.params, **get_photos_params}).json()
        dict_photos = {}
        for item in tqdm(req['response']['items']):
            photo_name = item['likes']['count']
            for photo in item['sizes']:
                if (photo['type'] == 'z' or photo['type'] == 'w' or
                        photo['type'] == 'y' or photo['type'] == 'x'):
                    if photo_name not in dict_photos:
                        dict_photos[photo_name] = [photo['url'],
                                                   photo['type'], item['date']]
                        print(dict_photos)
                        break
                    else:
                        photo_name = f'{photo_name}_{str(item["date"])}'
                        dict_photos[photo_name] = [photo['url'],
                                                   photo['type'], item['date']]
                        print(dict_photos)
                        break
            time.sleep(0.33)
        return dict_photos


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

if __name__ == '__main__':

    config = configparser.ConfigParser()  # через .ini файл
    config.read("tokens.ini")

    photos_quantity = input('Сколько фотографий вы бы хотели копировать?')
    vk_user_id = input('Введите user id или screen name')
    dir_name = input('В какую папку хотите положить фотографии?')
    VKTOKEN = config['VK']['token'].strip('"')
    YATOKEN = config['Yandex']['token'].strip('"')
    downloader = VKDownloader(VKTOKEN)
    uploader = YaUploader(YATOKEN)
    uploader.upload_photos(
        downloader.get_photos(vk_user_id, int(photos_quantity)), dir_name)
