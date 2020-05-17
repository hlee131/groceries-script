"Scrapes sayweee.com for food. Sends you email when found"""

import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ExpectedConditions

with open('secrets.txt', 'r') as file:
        SECRETS = file.readlines()

class Item():
    """Basic class to store information of not sold out items"""
    def __init__(self, price, image_link, name, link, num):
        self.price = price
        self.image_link = image_link
        self.link = link
        self.name = name
        self.id = num

class Scraper():
    """Represents scraper process, class is used because it allows threads to access common constants"""
    def __init__(self):
        """instantiating webdriver instance and defining constants"""
        chrome_path = r'..\chromedriver.exe'
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('log-level=3')
        self.driver = webdriver.Chrome(executable_path=chrome_path, chrome_options=chrome_options)

        self.LINK_TEXTS = ['Fruit', 'Greens', 'Meat', 'Seafood', 'Restaurant',
                'Dim Sum', 'Ready-Made', 'Bakery', 'Snacks', 'Dairy',
                'Dried Goods', 'Seasonings', 'Personal Care', 'Groceries']
        self.food_found = set()
        self.LINK = 'https://sayweee.com/en'
        self.PRODUCT_BASE_LINK = 'https://www.sayweee.com/product/view/'

    def click_out(self):
        """Simple function to click out of ad"""
        webdriver.ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()

    def sub_scrape(self, already_found, previously_found):
        """scraping individual tabs of category"""
        products = self.driver.find_elements_by_class_name('product-media')
        for product in products:
            try:
                _ = product.find_element_by_css_selector('div.product-unavailable')

            except NoSuchElementException:    
                price = f"${product.get_attribute('data-product-price')}"
                image_link = product.find_element_by_class_name('lazy-b').get_attribute('src')
                name = product.find_element_by_class_name('product-title').text.strip()
                product_id = product.get_attribute('data-product-id')
                link = self.PRODUCT_BASE_LINK + product_id
                if name == '':
                    pass

                else:
                    if product_id in already_found:
                        pass

                    else:
                        if product_id not in previously_found:
                            product = Item(price, image_link, name, link, product_id)
                            self.food_found.add(product)
                            already_found.append(product_id)
                            print(product.name)

                        else: pass

        return already_found

    def record(self):
        """Records found food into previously_found.txt"""
        with open('previously_found.txt', 'w') as file:
            for product in self.food_found:
                file.write(f'{product.id}\n')

    def scrape_page(self):
        """Used to find non-sold out food

        1. Iterates through filters
        2. Finds any food that isn't sold out
        """
        prev = []
        with open('previously_found.txt', 'r') as file:
            ids = file.readlines()
            for i in ids:
                i = i.strip('\n')
                prev.append(i)

        already_found = self.sub_scrape([], prev)
        try:
            filter_list = self.driver.find_element_by_class_name('list-filter')
            filters = filter_list.find_elements_by_css_selector('.filter-item')

            for filt in filters:                 
                filt.click()
                already_found = self.sub_scrape(already_found, prev)

        finally:
            return

    def main(self, link): 
        """Don't call me, call main_wrapper"""
        ZIP = SECRETS[0]
        self.driver.get(self.LINK)
        input = self.driver.find_element_by_id('zip_code')
        input.send_keys(ZIP)
        _ = self.driver.find_element_by_id('save-btn')

        # Click out of pop out ad 
        self.click_out()
        time.sleep(0.5)

        trying = True
        while trying:
            try:
                page = self.driver.find_element_by_link_text(link)
                page.click()
                self.scrape_page()
                return

            except:
                trying = True
                self.click_out()

    # Sends email notifying you of available products
    def send(self, products):
        if len(products) != 0:
            text = []
            for item in products:
                text.append(f'{item.name}\n{item.price}\n{item.link}')

            final_text = "\n\n".join(text)
            EMAIL_ADDRESS = SECRETS[1]
            EMAIL_PASSWORD = SECRETS[2]
            TARGET = SECRETS[3]
            message = MIMEMultipart('alternative')
            message['Subject'] = 'SayWeee Update'
            message['From'] = EMAIL_ADDRESS
            message['To'] = TARGET

            part1 = MIMEText(final_text, 'plain')
            message.attach(part1)

            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                smtp.send_message(message)

        else:
            print('Didnt send')

    def main_wrapper(self):
        """call this"""
        for link in self.LINK_TEXTS:
            self.main(link)

        self.record()
        self.send(self.food_found)
