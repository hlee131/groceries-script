"Scrapes sayweee.com for food. Sends you email when found"""

import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException

# We need to input a zip code for this to work
chrome_options = Options()
# chrome_options.add_argument('--headless')
driver = webdriver.Chrome(chrome_options=chrome_options)
LINK = 'https://sayweee.com/en'
PRODUCT_BASE_LINK = 'https://www.sayweee.com/product/view/'
with open('secrets.txt', 'r') as file:
    SECRETS = file.readlines()

ZIP = SECRETS[0]

class Item():
    """Basic class to store information of not sold out items"""
    def __init__(self, price, image_link, name, link, num):
        self.price = price
        self.image_link = image_link
        self.link = link
        self.name = name
        self.id = num

def click_out():
    """Simple function to click out of modal"""
    webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()

def sub_scrape(already_found, previously_found):
    """scraping individual tabs"""
    products = driver.find_elements_by_class_name('product-media')
    for product in products:
        try:
            tag = product.find_element_by_css_selector('div.sold-out-tag')

        except NoSuchElementException:    
            price = f"${product.get_attribute('data-product-price')}"
            image_link = product.find_element_by_class_name('lazy-b').get_attribute('src')
            name = product.find_element_by_class_name('product-title').text.strip()
            product_id = product.get_attribute('data-product-id')
            link = PRODUCT_BASE_LINK + product_id
            if name == '':
                pass

            else:
                if product_id in already_found:
                    pass

                else:
                    if product_id not in previously_found:
                        product = Item(price, image_link, name, link, product_id)
                        food_found.add(product)
                        already_found.append(product_id)
                        print(product.name)

                    else: pass

    return already_found

def record():
    """Records found food into previously_found.txt"""
    with open('previously_found.txt', 'w') as file:
        for product in food_found:
            file.write(f'{product.id}\n')

def scrape_page():
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

    already_found = sub_scrape([], prev)
    try:
        filter_list = driver.find_element_by_class_name('list-filter')
        filters = filter_list.find_elements_by_css_selector('.filter-item')

        back_times = len(filters)
        for filter in filters:                 
            filter.click()
            already_found = sub_scrape(already_found, prev)

        return back_times

    except:
        return 1
        
driver.get(LINK)
input = driver.find_element_by_id('zip_code')
input.send_keys(ZIP)
submit_button = driver.find_element_by_id('save-btn')

# Wait for page to load
time.sleep(1)

# Click out of pop out ad 
click_out()

LINK_TEXTS = ['Fruit']
""", 'Greens', 'Meat', 'Seafood',
            'Dim Sum', 'Ready-Made', 'Bakery', 'Snacks', 'Dairy',
            'Dried Goods', 'Seasonings', 'Personal Care', 'Groceries']"""

food_found = set()

# Clicks on each predefined hyperlink
for link in LINK_TEXTS:
    page = driver.find_element_by_link_text(link)
    page.click()
    time.sleep(0.5)   # wait for page to load
    back_times = scrape_page()
    back_button = driver.find_element_by_class_name('back')
    for i in range(back_times):
        back_button.click()

    time.sleep(1)

    click_out()

record()

# Sends email notifying you of available products
def send(products):
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

send(food_found)



