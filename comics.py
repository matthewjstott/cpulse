import requests
from bs4 import BeautifulSoup as soup
import datetime
import os
from pushover import Pushover as pusho
import pickle
import validators

from dotenv import load_dotenv
import pulse_util as util
import pulse as pul

    
class ForbiddenPlanet:
    
    
    def __init__(self, get_live_sitemap = True, verbose = False):
        
        self.sitemap_home = 'https://forbiddenplanet.com/sitemap.xml'
        self.webpage_home = 'https://forbiddenplanet.com'
        self.verbose = verbose
        if get_live_sitemap:
            self.products = self.get_current_products()
            self.save_current_stock()
            
        else:
            self.products = self.load_current_stock()

        self.pulse = pul.Pulse()
    
    def get_max_product_pages(self):

        res = requests.get(self.sitemap_home)
        data = res.text
        sres = soup(data, features="lxml")
        relivant_pages = [x.text.strip() for x in sres.findAll('loc') if '/sitemap-products' in x.text]
        max_page = max([int(x.split('?p=')[-1].strip()) for x in relivant_pages if '?p=' in x])

        return max_page
        
    def get_current_products(self):
    
        current_max_pages = self.get_max_product_pages()
        products = []
        for page in range(1,current_max_pages+1):
            if self.verbose:
                print(f'Currently parsing page {page} of {current_max_pages}...')
            res = requests.get(f'https://forbiddenplanet.com/sitemap-products.xml?p={page}').text
            sres = soup(res)
            products.append([x.loc.text.strip() for x in sres.findAll('url')])

        flattened_products = [i for j in products for i in j]
        return flattened_products
        
    def get_stock_count(self, product_url):
        
        res = soup(requests.get(product_url).text, features="html.parser")
        stock_number = [x.string.strip().split('stock_count":')[-1].split(',')[0] for x in res.find_all('script') if x.string if 'stock_count' in x.string]
        stock_number, = [float('nan') if not x.isdigit() else int(x) for x in stock_number]
        return stock_number
    
    def hyphen_wrapper(self, text):
        if len(text.split()) == 1 and '*' in text:
            return text.replace('*','')
        else:
            return '-'+'-'.join(text.split())

    def set_comic_scope(self, series, issue_number = None, artist = None, cover=None, variant = False, single_issue = True):
    
        match_strings = []
        match_strings.append(self.hyphen_wrapper(series))
        if single_issue and issue_number:
            match_strings.append(self.hyphen_wrapper(str(issue_number)))
        if artist:
            match_strings.append(self.hyphen_wrapper(artist))
        if cover:
            match_strings.append(self.hyphen_wrapper(f'cover-{cover}'))
        if variant:
            match_strings.append(self.hyphen_wrapper('variant'))

        return match_strings
    
    
    def exercute_search_vectors(self, comic_scope, search_vector = 'sitemap'):
        
        if search_vector == 'sitemap':
            current_products = self.products
            matching_comics = [url for url in current_products if all(feature in url for feature in comic_scope)]
            return matching_comics
            
    def return_comic_url(self, comic_scope):
        url, = self.exercute_search_vectors(comic_scope)
        return url

    def save_current_stock(self):
        open_file = open('fp_resources/current_stock', 'wb')
        pickle.dump(self.products, open_file)
        open_file.close()

    def load_current_stock(self):
        open_file = open('fp_resources/current_stock', 'rb')
        loaded_list = pickle.load(open_file)
        open_file.close()
        return loaded_list


    def format_watchlist_notification(self, comics: dict) -> str:

        message = self.initiate_message()

        for comic_dict in list(comics.values()):
            for comic_title in comic_dict.items():

                stock = self.get_stock_count(comic_title[-1])
                tiny_url = util.make_tiny(comic_title[-1])
                if stock > 0:
                    message.append(
                        f"<font color='orange'>{comic_title[0]}</font> \n Currently <font color='green'>IN</font> stock! :) with a Qty: <b>{stock}</b> \n <a href='{tiny_url}'>Buy now!</a>")
                    self.message_line(message, line_type='comic_seperator')
                else:
                    message.append(
                        f"<font color='orange'>{comic_title[0]}</font> \n Currently <font color='red'>NOT</font> in stock! :( ")
                    self.message_line(message, line_type='comic_seperator')

        message = '\n'.join(message)
        return message

    def run_watchlist_notification(self, specific_list=None):
        comics = util.load_json_file(list_type='watchlist')
        notification = self.format_watchlist_notification(comics)

        if specific_list:
            self.send_notification(notification, list_title=specific_list, notification_type='watchlist')
        else:
            self.send_notification(notification, list_title='Total Watch', notification_type='watchlist')


    def format_stock_notification(self, comics: dict) -> str:

        message = self.initiate_message()

        for comic_dict in list(comics.values()):
            for comic_title in comic_dict.items():

                stock = self.get_stock_count(comic_title[-1])
                tiny_url = self.make_tiny(comic_title[-1])
                if stock > 0:
                    message.append(
                        f"<font color='orange'>{comic_title[0]}</font> \n Looks to be back <font color='green'>IN</font> stock! :) with a Qty: <b>{stock}</b> \n <a href='{tiny_url}'>Buy now!</a>")
                    self.message_line(message, line_type='comic_seperator')
                else:
                    continue

        message = '\n'.join(message)
        return message

    def run_stocklist_notification(self, specific_list=None):
        comics = util.load_json_file(list_type='stocklist')
        notification = self.format_oos_notification(comics)

        if specific_list:
            self.send_notification(notification, list_title=specific_list, notification_type='ooslist')
        else:
            self.send_notification(notification, notification_type='ooslist')

    def format_livelist_notification(self, comics: dict) -> str:

        message = self.initiate_message()

        for comic_dict in list(comics.values()):
            for comic_title in comic_dict.items():
                live_status = self.exercute_search_vectors(comic_title[-1])

                if len(live_status) == 1:
                    #stock = self.get_stock_count(live_status[0])
                    stock = 1
                    tiny_url = util.make_tiny(live_status[0])
                    if stock > 0:
                        message.append(
                            f"<font color='orange'>{self.scope_format_convertion(comic_title[-1])}</font> \n is <font color='green'>LIVE</font> and <font color='green'>IN STOCK</font> Qty: <b>{stock}</b> \n <a href='{tiny_url}'>Buy now!</a>")
                        self.message_line(message, line_type='comic_seperator')
                    elif stock == 0:
                        message.append(
                            f"<font color='gold'>{self.scope_format_convertion(comic_title[-1])}</font> \n is <font color='green'>LIVE</font> but <font color='red'>OOS</font> \n <a href='{tiny_url}'>Watch here!</a>")
                        self.message_line(message, line_type='comic_seperator')
                elif not live_status:
                    message.append(
                        f"<font color='orange'>{self.scope_format_convertion(comic_title[-1])}</font> \n is <font color='red'>NOT</font> live yet.")
                    self.message_line(message, line_type='comic_seperator')

        message = '\n'.join(message)
        return message

    def run_livelist_notification(self, specific_list=None):
        comics = util.load_json_file(list_type='livelist')
        notification = self.format_livelist_notification(comics)

        if specific_list:
            self.send_notification(notification, list_title=specific_list, notification_type='livelist')
        else:
            self.send_notification(notification, list_title='Total Watch', notification_type='livelist')

    def scope_format_convertion(self, comic_scope: list) -> str:
        comic_scope = [x.replace('-',' ').title() for x in comic_scope]
        return ' -'.join(comic_scope).strip()

    def formulate_comic_dict(self, comic_list, comic_name, comic_data):
        if comic_list not in ('watchlist', 'stocklist', 'livelist'):
            raise NameError("Please ensure you have selected either watchlist, stocklist or livelist.")
        else:
            self.comic_format_check(comic_list, comic_data)

        return {comic_list.title(): {comic_name: comic_data}}

    def comic_format_check(self, comic_list, comic_data):
        if comic_list in ('watchlist', 'stocklist'):
            assert validators.url(comic_data)
        elif comic_list == 'livelist':
            assert all(isinstance(comic_str, str) for comic_str in comic_data) and isinstance(comic_data, list)

    def formulate_comic_data(self, comic_list, comic_data):
        if comic_list == 'livelist':
            set_comic_scope(comic_data)

        return comic_data

    def add_comic(self, comic_list, comic_name, comic_data):

        comic_data = self.formulate_comic_data(comic_list, comic_data)
        comic_dict = self.formulate_comic_dict(comic_list, comic_name, comic_data)
        current_comics = util.load_json_file(list_type=comic_list)
        updated_comics = util.merge_dict_objects(current_comics, comic_dict)
        util.save_to_json(updated_comics, list_type=comic_list)

    def initiate_message(self):

        message = []
        self.message_line(message, line_type='message_header')
        message.append(f'<b>{datetime.datetime.now().strftime("%d-%B-%Y %H:%M:%S")}</b>')
        self.message_line(message, line_type='message_header')

        return message

    def message_line(self, message, line_type=None):
        line_types = {"message_header": "==============================",
                      "comic_seperator": "----------------------------------"}
        message.append(line_types[line_type])
        return message

    def send_notification(self, notification: str, list_title: str = '', notification_type: str = 'watchlist') -> None:
        msg = self.pulse.po.msg(notification)
        titles = {'watchlist':f"{list_title.upper()} STOCK CHECK", 'ooslist':"OOS STOCK ALERT", 'livelist': "LIVE TITLE ALERT"}
        msg.set("title", titles[notification_type])
        msg.set("html",1)
        self.pulse.po.send(msg)

class Pulse:
    
    def __init__(self, **kwargs):
    
        super().__init__(**kwargs)
        load_dotenv()
        api_key = os.getenv("PUSHOVER_API_KEY")
        user_key = os.getenv("PUSHOVER_USER_KEY")
        self.po = pusho(api_key)
        self.po.user(user_key)
        
        
    def send_notification(self, notification: str, list_title: str = '', notification_type: str = 'watchlist') -> None:
        msg = self.po.msg(notification)
        titles = {'watchlist':f"{list_title.upper()} STOCK CHECK", 'ooslist':"OOS STOCK ALERT", 'livelist': "LIVE TITLE ALERT"}
        msg.set("title", titles[notification_type])
        msg.set("html",1)
        self.po.send(msg)

    def initiate_message(self):

        message = []
        self.message_line(message, line_type = 'message_header')
        message.append(f'<b>{datetime.datetime.now().strftime("%d-%B-%Y %H:%M:%S")}</b>')
        self.message_line(message, line_type = 'message_header')

        return message

    def message_line(self, message, line_type = None):
        line_types = {"message_header":"==============================", "comic_seperator":"----------------------------------"}
        message.append(line_types[line_type])
        return message
    


        
        
        
        
