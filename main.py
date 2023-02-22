import requests
import json
from tqdm import tqdm


class VK:

    def __init__(self, access_token, user_id, photo_quantity=5, version='5.131'):
        self.token = access_token
        self.id = user_id
        self.version = version
        self.quan = photo_quantity
        self.params = {'access_token': self.token, 'v': self.version}

    def photo_info(self):
        url = 'https://api.vk.com/method/photos.get'
        params = {'owner_id': self.id, 'album_id': 'wall', 'extended': '1', 'photo_sizes': '1'}
        response = requests.get(url, params={**self.params, **params})
        return response.json()

    def photo_sorted(self):
        dic = {}
        for item in self.photo_info()['response']['items']:
            filename = f"{item['likes']['count']}"
            filename_time = f"{item['likes']['count']}_{item['date']}"
            size_photo = {'s': 1, 'm': 2, 'o': 3, 'p': 4, 'q': 5, 'r': 6, 'x': 7, 'y': 8, 'z': 9, 'w': 10}
            file_url = max(item['sizes'], key=lambda x: size_photo[x['type']])['url']
            size = max(item['sizes'], key=lambda x: size_photo[x['type']])['type']
            if filename not in dic.keys():
                dic[filename] = {'size': size, 'url': file_url}
            else:
                dic[filename_time] = {'size': size, 'url': file_url}
        photo_dic = {k: dic[k] for k in list(dic)[:self.quan]}
        return photo_dic


class Ya:

    def __init__(self, ya_token, folder_name):
        self.token = ya_token
        self.folder = folder_name
        self.uri = 'https://cloud-api.yandex.net'
        self.headers = {'Content-Type': 'application/json', 'Authorization': f'OAuth {self.token}'}

    def photo_upload(self):
        requests.put(self.uri + '/v1/disk/resources', headers=self.headers, params={'path': self.folder})
        log_file = []
        for file in tqdm(vk.photo_sorted(), ncols=80, desc='Процесс копирования'):
            resp_file = requests.post(self.uri + '/v1/disk/resources/upload', headers=self.headers,
                                      params={'path': f'{self.folder}/{file}.jpg',
                                              'url': f"{vk.photo_sorted()[file]['url']}"})
            if resp_file.status_code == 202:
                log_file.append({'file_name': file, 'size': vk.photo_sorted()[file]['size']})
        with open("log_file.json", "w") as write_file:
            json.dump(log_file, write_file)
        return log_file

access_token = ... # Токен ВК

user_id = ... # ID пользователя ВК

ya_token = ... # Токен Yandex

folder_name = 'vk_upload' # Имя папки на Яндекс-диск

vk = VK(access_token, user_id)
ya = Ya(ya_token, folder_name)

print(ya.photo_upload())
