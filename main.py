import json
import configparser
import time

import requests
from tqdm import tqdm


class VK:

    def __init__(self, photo_quantity, version):
        self.token = read_ini()['Tokens']['vk_token']
        self.id = read_vk_id()
        self.version = version
        self.quan = photo_quantity
        self.params = {'access_token': self.token, 'v': self.version}

    def photo_info(self):
        url = 'https://api.vk.com/method/photos.get'
        params = {'owner_id': self.id, 'album_id': 'profile',
                  'extended': '1', 'photo_sizes': '1'
                  }
        response = requests.get(url, params={**self.params, **params})
        return response.json()

    def photo_sorted(self):
        dic = {}
        for item in self.photo_info()['response']['items']:
            filename = f"{item['likes']['count']}"
            t = time.localtime(item['date'])
            filename_time = f"{item['likes']['count']}_{t.tm_hour}_" \
                            f"{t.tm_min}_{t.tm_mday}_{t.tm_mon}_{t.tm_year}"
            size_photo = {'s': 1, 'm': 2, 'o': 3, 'p': 4, 'q': 5,
                          'r': 6, 'x': 7, 'y': 8, 'z': 9, 'w': 10
                          }
            file_url = max(item['sizes'],
                           key=lambda x:size_photo[x['type']])['url']
            size = max(item['sizes'],
                       key=lambda x: size_photo[x['type']])['type']
            if filename not in dic.keys():
                dic[filename] = {'size': size, 'url': file_url}
            else:
                dic[filename_time] = {'size': size, 'url': file_url}
        photo_dic = {k: dic[k] for k in list(dic)[:self.quan]}
        return photo_dic


class Ya:

    def __init__(self, folder_name):
        self.token = read_ini()['Tokens']['ya_token']
        self.folder = folder_name
        self.uri = 'https://cloud-api.yandex.net'
        self.headers = {'Content-Type': 'application/json',
                        'Authorization': f'OAuth {self.token}'
                        }

    def photo_upload(self):
        requests.put(self.uri + '/v1/disk/resources',
                     headers=self.headers,
                     params={'path': self.folder}
                     )
        log_file = []
        for file in tqdm(vk.photo_sorted(), ncols=80, desc='Процесс копирования'):
            resp_file = requests.post(self.uri + '/v1/disk/resources/upload',
                                      headers=self.headers,
                                      params={'path': f'{self.folder}/{file}.jpg',
                                              'url': f"{vk.photo_sorted()[file]['url']}"}
                                      )
            if resp_file.status_code == 202:
                log_file.append({'file_name': file,
                                 'size': vk.photo_sorted()[file]['size']}
                                )
        write_log(log_file)
        return log_file


def write_log(log_file):
    with open("log_file.json", "w") as write_file:
        json.dump(log_file, write_file)


def read_ini():
    config = configparser.ConfigParser()
    config.read('settings.ini')
    return config


def read_vk_id():
    url = 'https://api.vk.com/method/users.get'
    response = requests.get(url, params={'access_token': read_ini()['Tokens']['vk_token'],
                                         'v': read_ini()['Versions']['vk'],
                                         'user_ids': input('Укажите ID или screen_name пользователя: ')})
    return response.json()['response'][0]['id']


vk = VK(int(input('Укажите количество фотографий: ')), read_ini()['Versions']['vk'])
ya = Ya('vk_upload')

print(ya.photo_upload())
