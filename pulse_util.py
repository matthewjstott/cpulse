import contextlib
import json

from urllib.parse import urlencode
from urllib.request import urlopen



def make_tiny(url: str) -> str:
    request_url = ('http://tinyurl.com/api-create.php?' + urlencode({'url': url}))
    with contextlib.closing(urlopen(request_url)) as response:
        return response.read().decode('utf-8 ')

def save_to_json(data, list_type='watchlist'):
    with open(f'comic_lists/{list_type}.json', 'w') as f:
        json.dump(data, f)

def load_json_file(list_type='watchlist'):
    f = open(f'comic_lists/{list_type}.json')
    data = json.load(f)
    f.close()
    return data


def merge_dict_objects(dict_a, dict_b, path=None):

    dict_b = {k.title() :v for k ,v in dict_b.items()}
    if path is None:
        path = []
    for key in dict_b:
        if key in dict_a:
            if isinstance(dict_a[key], dict) and isinstance(dict_b[key], dict):
                merge_dict_objects(dict_a[key], dict_b[key], path + [str(key)])
            elif dict_a[key] == dict_b[key]:
                pass
            else:
                raise Exception('Conflict at %s' % '.'.join(path + [str(key)]))
        else:
            dict_a[key] = dict_b[key]
    return dict_a