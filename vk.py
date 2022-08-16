import requests
from tqdm import tqdm
import time


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