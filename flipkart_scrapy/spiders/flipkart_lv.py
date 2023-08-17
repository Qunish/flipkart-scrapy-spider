import scrapy
from selenium.webdriver.common.by import By
import random
import time
from ..items import FlipkartScrapyItem_LV
import pymongo

DRIVER_FILE_PATH = "/Users/qunishdash/Documents/chromedriver_mac64/chromedriver"
USER_AGENT_LIST = ['Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36',
                    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:86.0) Gecko/20100101 Firefox/86.0',
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:72.0) Gecko/20100101 Firefox/72.0',
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36',
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36'
                    ]

class FlipkartLvSpider(scrapy.Spider):
    name = "flipkart_lv"
    handle_https_status_list = [403]
    start_urls = [
        "https://www.flipkart.com/search?p[]=facets.brand%255B%255D%3D%2540home%2Bby%2BNilkamal&sid=anx&otracker=CLP_filters&otracker=nmenu_sub_Home%20%26%20Furniture_0_%40home"
    ]

    # def __init__(self):
    #     self.conn = pymongo.MongoClient(
    #         "localhost",
    #         27017
    #     )
    #     db = self.conn["flipkart_scrapy_db"]
    #     self.collection = db["home_lv"]

    def get_chrome_driver(self, headless_flag):
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        if headless_flag:
            # in case you want headless browser
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--start-maximized")
            # chrome_options.add_experimental_option('prefs', {'headers': headers}) # if you want to add custom header
            chrome_options.add_argument("user-agent={}".format(random.choice(USER_AGENT_LIST)))
            driver = webdriver.Chrome(options=chrome_options) 
        else:
            # in case  you want to open browser
            chrome_options = Options()
            # chrome_options.add_experimental_option('prefs', {'headers': headers}) # if you want to add custom header
            chrome_options.add_argument("--start-maximized")
            chrome_options.add_argument("user-agent={}".format(random.choice(USER_AGENT_LIST)))
            chrome_options.headless = False
            driver = webdriver.Chrome(options=chrome_options)

        return driver

    def parse(self, response):
        if response.status == 403:
            self.logger.warning("Status 403 - but chill we are handling using selenium driver.")

        driver = self.get_chrome_driver(headless_flag=False)
        driver.get(response.url)
        
        items = FlipkartScrapyItem_LV()

        # Extract data using Selenium and yield items
        all_cards = driver.find_elements(By.CSS_SELECTOR, "._4ddWXP")

        for card in all_cards:
            try:
                product_name = card.find_element(By.CSS_SELECTOR, ".s1Q9rs").text
            except Exception as e:
                product_name = ''
            try:
                product_price = card.find_element(By.CSS_SELECTOR, "._30jeq3").text
            except Exception as e:
                product_price = ''
            try:
                product_original_price = card.find_element(By.CSS_SELECTOR, "._3I9_wc").text
            except Exception as e:
                product_original_price = ''
            try:
                product_discount_percentage = card.find_element(By.CSS_SELECTOR, "._3Ay6Sb span").text
            except Exception as e:
                product_discount_percentage = ''
            try:
                product_image_url = card.find_element(By.CSS_SELECTOR, "._396cs4").get_attribute("src")
            except Exception as e:
                product_image_url = ''
            try:
                product_url = card.find_element(By.CSS_SELECTOR, ".s1Q9rs").get_attribute("href")
            except Exception as e:
                product_url = ''

            items["product_name"] = product_name
            items["product_price"] = product_price
            items["product_original_price"] = product_original_price
            items["product_discount_percentage"] = product_discount_percentage
            items["product_image_url"] = product_image_url
            items["product_url"] = product_url

            # self.collection.insert_one(dict(items))

            yield items
        next_page = response.css("._1LKTO3::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback = self.parse)

        driver.quit()

