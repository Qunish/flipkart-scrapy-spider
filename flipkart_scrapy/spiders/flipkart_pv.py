import scrapy
from selenium.webdriver.common.by import By
import random
import pymongo
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

DRIVER_FILE_PATH = "/Users/qunishdash/Documents/chromedriver_mac64/chromedriver"
USER_AGENT_LIST = ['Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36',
                    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:86.0) Gecko/20100101 Firefox/86.0',
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:72.0) Gecko/20100101 Firefox/72.0',
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36',
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36'
                    ]

class FlipkartPvSpider(scrapy.Spider):
    name = "flipkart_pv"
    handle_httpstatus_list = [403]
    # def __init__(self):
    #     self.conn = pymongo.MongoClient(
    #         "localhost",
    #         27017
    #     )
    #     db = self.conn["ajio_scrapy_db"]
    #     self.collection = db["fengshui_lv"]
    #     self.pvcollection = db["fengshui_pv"]
    #     self.start_urls = [document['url'] for document in self.collection.find()]
    start_urls = ["https://www.flipkart.com/soft-bean-bag-2-5-kg-filler/p/itm8e15d6f381bb8?pid=BBFFTPKJQBSYMMNG&lid=LSTBBFFTPKJQBSYMMNG7CJGUJ&marketplace=FLIPKART&store=wwe&srno=b_1_18&otracker=CLP_filters&fm=organic&iid=en_DTPoSXTRhl1iIWqlJr5u8IICrFOtOptZhZgf1v6y5ZznC0DCBvO_pSlr_G0EvZSoQXJvWKRdYc1WuSkgWxLKzg%3D%3D&ppt=browse&ppn=browse&ssid=770xmhkxk00000001691812472153"]

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
    
    def get_product_data(self, url):
        # Initialize the WebDriver here
        driver = self.get_chrome_driver(headless_flag=False)
        driver.get(url)

        try:
            try:
                product_highlights = driver.find_element(By.CSS_SELECTOR, '._2cM9lP').text
            except Exception as e:
                product_highlights = ''
            try:
                product_description = driver.find_element(By.CSS_SELECTOR, '.RmoJUa').text
            except Exception as e:
                product_description = ''
            try:
                product_specification = driver.find_element(By.CSS_SELECTOR, '._1UhVsV').text
            except Exception as e:
                product_specification = ''
            try:
                product_rating_reviews = driver.find_element(By.CSS_SELECTOR, '._3_L3jD').text
            except Exception as e:
                product_rating_reviews = ''

            data = {
                "activity_url": url,
                "product_highlights": product_highlights,
                "product_description": product_description,
                "product_specification": product_specification,
                "product_rating_reviews": product_rating_reviews
            }
            return data
        except Exception as e:
            print("Error while extracting activity data:", e)
            return None
        finally:
            driver.quit()    

    def parse(self, response):
        if response.status == 403:
            self.logger.warning("Status 403 - but chill we are handling using selenium driver.")
        url = response.url

        product_details = self.get_product_data(url)
        print(product_details)
        # if product_details:
        #     self.pvcollection.update_one({"url": url}, {"$set": product_details}, upsert=True)
