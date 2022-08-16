import configparser
from vk import VKDownloader
from ya_disk import YaUploader


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
