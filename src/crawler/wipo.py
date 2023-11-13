import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

from src.database.mongo import MongoDB
from src.crawler.base_crawler import BaseCrawler
from src.utils.selenium_utils import get_driver, filter_duplicated_link

class WipoCrawler(BaseCrawler):
    def __init__(self, config, db, out_dir):
        super(BaseCrawler, self).__init__()
        self.config = config
        self.db = MongoDB()
        self.db.set_database(db_name=db)
        self.out_dir = out_dir
    
    def crawl_links(self, driver, surname, secs, save_path="src_link/links.txt"):
        driver.get('https://patentscope.wipo.int/search/en/search.jsf')
        time.sleep(secs)

        search_field = driver.find_element(
            By.ID, "simpleSearchForm:fpSearch:input")
        search_field.send_keys('IC:("G06F 17") and IN:({})'.format(surname))
        # search_field.send_keys(
        #     'IC:("G06F 17") and ALLNUM:(VN) and IN:({})'.format(surname))
        search_field.send_keys(Keys.ENTER)
        time.sleep(secs)

        # num docs per page
        element_select = Select(driver.find_element(
            By.ID, "resultListCommandsForm:perPage:input"))
        all_options = [o.get_attribute('value')
                    for o in element_select.options]
        selected_value = all_options[-2]
        element_select.select_by_value(selected_value)  # 100 PER PAGE
        time.sleep(secs)

        results_count = driver.find_element(
            By.XPATH, "//span[@class='results-count']").text.split()[0].replace(',', '')
        print('{}: {}'.format(surname, results_count))
        num_pages = int((int(results_count) / int(selected_value)))
        # print(num_pages.split('/')[-1].strip())
        time.sleep(secs)

        links = []

        for page in range(1, num_pages + 2):
            try:
                print('Page: {}'.format(page))

                next_page = driver.find_element(
                    By.XPATH, "//a[@title='Click to go to a specific page']")
                next_page.send_keys(Keys.ENTER)
                time.sleep(secs)
                pagination_field = driver.find_element(
                    By.CLASS_NAME, "ps-paginator-modal--input")
                pagination_field.clear()
                time.sleep(secs)
                pagination_field.send_keys(str(page))
                time.sleep(secs)
                pagination_field.send_keys(Keys.ENTER)
                time.sleep(secs)

                # get links paper
                element_link = [elem.get_attribute(
                    'href') for elem in driver.find_elements(By.TAG_NAME, "a")]
                time.sleep(secs)

                links_temp = []
                for i in element_link:
                    if 'patentscope.wipo.int/search/en/detail.jsf?' in str(i):
                        links_temp.append(str(i))

                links_temp = filter_duplicated_link(links_temp)

                with open(save_path, 'a') as f:
                    for i in links_temp:
                        f.write(i + '\n')
                        links.append(i)
                time.sleep(secs)
            except:
                continue

        return links

    def crawl_docs(self, driver, surname, secs, save_path="src_link/links.txt"):
        driver.get('https://patentscope.wipo.int/search/en/search.jsf')
        time.sleep(secs)

        search_field = driver.find_element(
            By.ID, "simpleSearchForm:fpSearch:input")
        search_field.send_keys('IC:("G06F 17") and IN:({})'.format(surname))
        # search_field.send_keys(
        #     'IC:("G06F 17") and ALLNUM:(VN) and IN:({})'.format(surname))
        search_field.send_keys(Keys.ENTER)
        time.sleep(secs)

        # num docs per page
        element_select = Select(driver.find_element(
            By.ID, "resultListCommandsForm:perPage:input"))
        all_options = [o.get_attribute('value')
                    for o in element_select.options]
        selected_value = all_options[-2]
        element_select.select_by_value(selected_value)  # 100 PER PAGE
        time.sleep(secs)

        results_count = driver.find_element(
            By.XPATH, "//span[@class='results-count']").text.split()[0].replace(',', '')
        print('{}: {}'.format(surname, results_count))
        num_pages = int((int(results_count) / int(selected_value)))
        # print(num_pages.split('/')[-1].strip())
        time.sleep(secs)

        links = []

        for page in range(1, num_pages + 2):
            try:
                print('Page: {}'.format(page))

                next_page = driver.find_element(
                    By.XPATH, "//a[@title='Click to go to a specific page']")
                next_page.send_keys(Keys.ENTER)
                time.sleep(secs)
                pagination_field = driver.find_element(
                    By.CLASS_NAME, "ps-paginator-modal--input")
                pagination_field.clear()
                time.sleep(secs)
                pagination_field.send_keys(str(page))
                time.sleep(secs)
                pagination_field.send_keys(Keys.ENTER)
                time.sleep(secs)

                # get links paper
                element_link = [elem.get_attribute(
                    'href') for elem in driver.find_elements(By.TAG_NAME, "a")]
                time.sleep(secs)

                links_temp = []
                for i in element_link:
                    if 'patentscope.wipo.int/search/en/detail.jsf?' in str(i):
                        links_temp.append(str(i))

                links_temp = filter_duplicated_link(links_temp)

                with open(save_path, 'a') as f:
                    for i in links_temp:
                        f.write(i + '\n')
                        links.append(i)
                time.sleep(secs)
            except:
                continue

        return links
