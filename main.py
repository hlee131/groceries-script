import time
import smtplib
from email.message import EmailMessage
from email.utils import make_msgid

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

# We need to input a zip code for this to work
driver = webdriver.Chrome()
LINK = 'https://sayweee.com/en'
PRODUCT_BASE_LINK = 'https://www.sayweee.com/product/view/'
with open('zip.txt', 'r') as file: 
    ZIP = file.readlines()[0]

class Item():
    """Basic class to store information of not sold out items"""
    def __init__(self, price, sold, image_link, name, left, link):
        self.price = price
        self.sold = sold
        self.image_link = image_link
        self.name = name
        self.left = left

def click_out():
    """Simple function to click out of modal"""
    webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()

def sub_scrape():
    """scraping individual tabs"""
    products = driver.find_elements_by_css_selector('.product-media')
    for product in products:
        try:
            product.find_element_by_class_name('sold-out-tag')

        except:    
            price = product.get_attribute('data-product-price')
            stats = product.find_element_by_class_name('product-statistics')
            image_link = product.find_element_by_class_name('lazy-b').get_attribute('src')
            name = product.find_element_by_class_name('product-title').text.strip()
            sold = stats.find_element_by_xpath('.//span[1]')
            product_id = product.get_attribute('data-product-id')
            link = PRODUCT_BASE_LINK + product_id
            try:
                left = stats.find_element_by_xpath('.//span[2]')  

            except: 
                left = None    

            product = Item(price, sold, image_link, name, left, link)
            food_found.append(product)
            print(product.name)

def scrape_page():
    """Used to find non-sold out food

    1. Iterates through filters
    2. Finds any food that isn't sold out
    """
    sub_scrape()
    filter_list = driver.find_element_by_class_name('list-filter')
    filters = filter_list.find_elements_by_css_selector('.filter-item')
    back_times = len(filters)
    for filter in filters:                 
        filter.click()
        sub_scrape()

    return back_times
        
driver.get(LINK)
input = driver.find_element_by_id('zip_code')
input.send_keys(ZIP)
submit_button = driver.find_element_by_id('save-btn')
submit_button.click()

# Wait for page to load
time.sleep(1)

# Click out of pop out ad 
click_out()

LINK_TEXTS = ['Fruit', 'Greens', 'Meat', 'Seafood',
            'Dim Sum', 'Ready-Made', 'Bakery', 'Snacks', 'Dairy',
            'Dried Goods', 'Seasonings', 'Personal Care', 'Groceries']

food_found = []

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

# Sends email notifying you of available products
def send(products):
    text = []
    non_hmtl_info = []
    divs = []
    with open('main_html.txt') as file: main_html = file.read()
    with open('extra_divs.txt') as file: extra_divs = file.read()

    for item in products:
        info = [item.name, item.price, item.link]
        non_hmtl_info.append(info)
        template = extra_divs % (item.image_link, item.name, item.price, item.link)
        divs.append(template)

    for l in non_hmtl_info:
        msg = '%s\n %s\n %s' % (l[0], l[1], l[2])
        text.append(msg)

    final_text = "\n\n".join(text)
    total_divs = "\n".join(divs)
    final_html = main_html % total_divs
    EMAIL_ADDRESS = ''
    EMAIL_PASSWORD = ''
    TARGET = ''
    message = EmailMessage()
    message['Subject'] = 'SayWeee Update'
    message['From'] = EMAIL_ADDRESS
    message['To'] = TARGET

    message.set_content("Here are the available items: \n\n %s") % final_text

    message.add_alternative(final_html, subtype='html')

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(message)



