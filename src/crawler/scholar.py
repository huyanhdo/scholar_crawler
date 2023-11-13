import os
import json
import time
import wget
import operator
import requests
from datetime import date
from selenium import webdriver
from selenium.webdriver.common.by import By
import re
from src.database.mongo import MongoDB
from src.crawler.base_crawler import BaseCrawler
from src.utils.bloomfilter_utils import Bloomfilter as BloomFilter
from src.utils.selenium_utils import get_driver,reset_driver_proxy
from bs4 import BeautifulSoup
from tqdm import tqdm
from urllib.parse import urlparse
from urllib.parse import parse_qs
from urllib.parse import quote_plus
import json
from src.crawler.utils import request_get_with_scraper
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from src.utils.handle_string import string_to_slug
import time
error = {
    "error": "Authentication failure: Not enough credits for this API call. Get a free API Key at https://app.webscrapingapi.com/register or upgrade your plan"
}


class GgscholarCrawler(BaseCrawler):
    def __init__(self, config, db, out_dir):
        super(BaseCrawler, self).__init__()
        self.config = config
        self.db = MongoDB()
        self.db.set_database(db_name=db)
        self.out_dir = out_dir
        self.saved_link = os.path.join(self.out_dir, "ggscholar")
        if not os.path.exists(self.saved_link):
            os.makedirs(self.saved_link)
        self.bloom_filter_expert = BloomFilter(self.saved_link + "/experts.txt")
        self.bloom_filter_org = BloomFilter(self.saved_link + "/organisations.txt")

        self.url_search_pattern = "https://scholar.google.com/citations?view_op=search_authors&hl=en&mauthors=label:{}+%2B+{}"
        self.author_url = "https://scholar.google.com/citations?user={}"

        # self.organization = set()

        with open(r"src\data\vietnamese_surnames.txt", "r") as surnames:
            self.surnames = surnames.read().split("\n")

        with open(r"src\data\fields_updated.txt", "r") as fields:
            self.fields = fields.read().split("\n")
        
        self.co_author_id = []

    def update_existed_informations(self, mode_save):
        # get_crawled_author_links -> crawl_authors -> update_author
        pass

    def crawl_new_informations(self, driver):
        # search_by_surname -> search_by_coauthor -> search_by_organization
        # filter_uncrawled_expert
        # return new_experts, new_organizations and save into db
        pass

    def _check_surname_is_vietnamese(self, name):
        surnames = [surname.lower() for surname in self.surnames]
        name = name.lower()
        for surname in surnames:
            if surname in name:
                return True
        return False

    def _get_user_id_from_url(self, path):
        parsed_url = urlparse(path)
        url_params = parse_qs(parsed_url.query)
        user_id = url_params["user"][0]
        return user_id

    def find_aff(self, soup):
        ils = soup.select(".gsc_prf_il")
        if len(ils) == 3:
            aff = ils[0]
            return aff.getText()
        else:
            candidates = [
                tag
                for tag in ils
                if tag.get("id") not in ["gsc_prf_ivh", "gsc_prf_int"]
            ]
            if len(candidates) > 0:
                return candidates[0].getText()
            else:
                return None

    def _parse_information_from_html(self, body):
        soup = BeautifulSoup(body, "html.parser")

        name_elm = soup.select_one("#gsc_prf_in")
        name = name_elm.getText()
        if not self._check_surname_is_vietnamese(name):
            return {}
        avatar_url = soup.select_one("#gsc_prf_pup-img")
        avatar_url = avatar_url["src"]

        aff = self.find_aff(soup)

        description_html = soup.select_one("#gsc_prf_ivh")
        description_html = description_html.decode_contents()

        expertise_html = soup.select("#gsc_prf_int > a")
        expertise_titles = [expertise.getText() for expertise in expertise_html]

        try:
            citations = int(soup.select(".gsc_rsb_std")[0].getText())

        except:
            citations = None

        data = {
            "name": name,
            "avatar_url": avatar_url,
            "organisation_name": aff,
            "description_html": description_html,
            "citations": citations,
            "expertise_names": expertise_titles,
            "name_slug": string_to_slug(name),
            "organisation_name_slug": string_to_slug(aff),
            "expertise_names_slug": [
                string_to_slug(expertise) for expertise in expertise_titles
            ],
        }
        return data

    def _parse_query_page(self, body, add_org=False):
        soup = BeautifulSoup(body, "html.parser")

        authors = []

        author_items = soup.select(".gsc_1usr")
        for author_item in author_items:
            name_elm = author_item.select_one(".gs_ai_name")

            profile_url = name_elm.select_one("a")["href"]
            user_id = self._get_user_id_from_url(profile_url)

            if not self.bloom_filter_expert.check_item_exist(user_id):
                self.bloom_filter_expert.add_new_items(user_id)
            else:
                continue

            name = name_elm.getText()
            if not self._check_surname_is_vietnamese(name):
                continue

            authors.append(user_id)

        next_page_btn = soup.select_one(".gs_btnPR")

        try:
            onclick = next_page_btn["onclick"]

            next_page_url = onclick.replace("window.location='", "")[:-1]
            next_page_url = next_page_url.replace("\\x3d", "=").replace("\\x26", "&")
            next_page_url = "https://scholar.google.com/" + next_page_url
        except Exception as err:
            next_page_url = None
        return authors, next_page_url

    def get_body(self,driver,url):
        # driver = reset_driver_proxy(driver)
        while True:
            try:
                time.sleep(1.5)
                driver.get(url)
                break
            except:
                print('error')
                continue    
        return driver.page_source
        # req = requests.get(url,headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.60'})
        # time.sleep(0.5)
        # print(req.status_code)
        # return req.content

    def _crawl_all_authors_by_searching(self, driver):
        """
        Crawl all authors given surname and tech fields
        """
        print("Crawl all authors given surname and tech fields")
        res = []

        research_fields = [x.strip() for x in self.fields if len(x.strip()) > 0]
        surnames = [x.strip() for x in self.surnames if len(x.strip()) > 0]

        research_fields = [x.lower().replace(" ", "_") for x in research_fields]

        list_of_request_urls = []

        for field in research_fields:
            for surname in surnames:
                url = self.url_search_pattern.format(field, surname)
                list_of_request_urls.append(url)

        driver = get_driver()
        check_time = time.time()
        for url in tqdm(list_of_request_urls):
            current_crawled_page_url = url
            print('reseting')
            if time.time() - check_time > 120:
                while True:
                    try:
                        driver = reset_driver_proxy(driver)
                        check_time = time.time()
                        break
                    except Exception as e: 
                        print(e)

            while True:
                body = self.get_body(driver,current_crawled_page_url)
                authors, next_page_url = self._parse_query_page(body, add_org=True)
                res = res + authors
                if next_page_url == None:
                    break
                else:
                    current_crawled_page_url = next_page_url
        result = []
        
        with open(r"src\data\scholar\authors_url.json", "w") as outfile:
            json.dump(res, outfile)

        check_time = time.time()

        for author in tqdm(res):
            if time.time() - check_time > 120:
                while True:
                    try:
                        driver = reset_driver_proxy(driver)
                        check_time = time.time()
                        break
                    except Exception as e: 
                        print(e)
            while True:
                try:
                    time.sleep(0.5)
                    data = self.crawl_all(driver, self.author_url.format(author), 1)
                    break
                except:
                    print('error')
                    continue
            result.append(data)
            
            # self.co_author_id += self._crawl_all_coauthors_id(driver,self.author_url.format(author))
  
        with open(r"src\data\scholar\authors.json", "w") as outfile:
            json.dump(result, outfile)

    def _crawl_all_coauthors(self, driver):
        print("Crawl all Vietnamese coauthors of given user")
        res = []
        coauthor_ids = self.co_author_id

        print("crawl_all_coauthors")
        for idx,id in enumerate(tqdm(coauthor_ids)):
            if idx % 200 == 0 and idx !=0 :
                time.sleep(180)
                 
            url = self.author_url.format(id)
            res.append(self.crawl_all(driver,url,1))
            # break 

        with open(r"src\data\scholar\coauthors.json", "w") as outfile:
            json.dump(res, outfile)

    def _crawl_all_coauthors_id(self, driver: webdriver.Chrome,url):
        """
        Crawl all Vietnamese coauthors of given user
        """
        driver.get(url)
        res = []
        view_all_btn = driver.find_elements(By.ID, "gsc_coauth_opn")
        if len(view_all_btn) > 0:
            view_all_btn[0].click()
            time.sleep(15)
            coauthors = driver.find_elements(By.CLASS_NAME, "gs_ai_name")
            for coauthor in coauthors:
                if not self._check_surname_is_vietnamese(coauthor.text):
                    continue
                coauthor_url = coauthor.find_elements(By.TAG_NAME, "a")
                id = coauthor_url[0].get_attribute("href")
                index = id.find("user=") + 5
                id = id[index : index + 12]
                if not self.bloom_filter_expert.check_item_exist(id):
                    self.bloom_filter_expert.add_new_items(id)
                else:
                    continue

                res.append(id)
        else:
            coauthors = driver.find_elements(By.TAG_NAME, "li")
            for coauthor in coauthors:
                coauthor_url = coauthor.find_elements(By.TAG_NAME, "a")
                if not self._check_surname_is_vietnamese(coauthor_url[0].text):
                    continue
                id = coauthor_url[0].get_attribute("href")

                index = id.find("user=") + 5
                id = id[index : index + 12]

                if not self.bloom_filter_expert.check_item_exist(id):
                    self.bloom_filter_expert.add_new_items(id)
                else:
                    continue
                res.append(id)
        return res

    def crawl_all_authors(self):
        if not os.path.exists(r"src\data\scholar"):
            os.makedirs(r"src\data\scholar")
        # driver = get_driver()
        driver = None
        self._crawl_all_authors_by_searching(driver)
        # self._crawl_all_coauthors(driver)
        # driver.quit()

        with open("src/data/scholar/authors.json", "r") as f:
            authors = json.loads(f.read())

        # with open("src/data/scholar/coauthors.json", "r") as f:
        #     coauthors = json.loads(f.read())

        # all_authors = authors + coauthors
        # with open(r"src\data\scholar\all_author.json", "w") as outfile:
        #     json.dump(all_authors, outfile)
        all_authors = authors
        self.db.set_collection('author')

        self.db.bulk_update_or_insert(all_authors)
        # return all_authors

    def crawl_all(self, driver, url, secs):
        result = {}
        
        driver.get("http://www.google.com")
        time.sleep(secs * 2)
        driver.get(url)
        time.sleep(secs)
      
        name = self._crawl_name(driver)
        org = self._crawl_org(driver)
        expertise_name = self._crawl_expertise_names(driver)
        result["user_id"] = url[url.find("user=") + 5 : url.find("user=") + 17]
        result["name"] = name
        result["org"] = org
    
        result["avatar_url"] = self._crawl_avatar_url(driver)
        result["expertise_names"] = expertise_name
        result["citations"], result["h_index"], result["i10_index"] = self._crawl_cite(
            driver
        )

        result["name_slug"] = string_to_slug(name)
        result["organisation_name_slug"] = string_to_slug(org)
        result["expertise_names_slug"] = [string_to_slug(expertise) for expertise in expertise_name]
        result["isDeleted"] = False
        result["haveVietnamesePeople"] = True
        return result

    def _crawl_name(self, driver: webdriver.Chrome):
        name = driver.find_element(By.XPATH, "//div[@id='gsc_prf_in']").get_attribute(
            "innerHTML"
        )

        name = name.strip()
        print("done name")
        return name

    def _crawl_org(self, driver: webdriver.Chrome):
        try:
            org = (
                driver.find_element(By.XPATH, "//div[@class='gsc_prf_il']")
                .find_element(By.TAG_NAME, "a")
                .get_attribute("innerHTML")
            )
        except:
            org = driver.find_element(
                By.XPATH, "//div[@class='gsc_prf_il']"
            ).get_attribute("innerHTML")

        org = org.strip()
        print("done org")
        return org

    def _crawl_homepage(self, driver: webdriver.Chrome):
        homepage = ""
        try:
            temp = driver.find_elements(By.XPATH, "//div[@class='gsc_prf_il']")[
                1
            ].find_element(By.TAG_NAME, "a")
            if temp.get_attribute("innerHTML").lower().replace(" ", "") == "homepage":
                homepage = temp.get_attribute("href")
        except:
            with open("src_link/no_homepage.txt", "a") as f:
                f.write(driver.current_url + "\n")
            pass

        print("done homepage")
        return homepage

    def _crawl_avatar_url(self, driver: webdriver.Chrome):
        avatar_url = driver.find_element(
            By.XPATH, "//img[@id='gsc_prf_pup-img']"
        ).get_attribute("src")

        avatar_url = avatar_url.strip()
        print("done avatar url")
        return avatar_url

    def _crawl_expertise_names(self, driver: webdriver.Chrome):
        expertise_names = []

        for exp in driver.find_element(
            By.XPATH, "//div[@id='gsc_prf_int']"
        ).find_elements(By.TAG_NAME, "a"):
            expertise_names.append(exp.get_attribute("innerHTML").strip())

        print("done expertise names")
        return expertise_names

    def _crawl_cite(self, driver: webdriver.Chrome):
        # citations = 0
        # h_index = 0
        # i10_index = 0

        # check_citations = driver.find_elements(By.XPATH, "//td[@class='gsc_rsb_std']")
        # check_h_index = driver.find_elements(By.XPATH, "//td[@class='gsc_rsb_std']")
        # check_i10_index = []
        info = driver.find_elements(By.XPATH, "//td[@class='gsc_rsb_std']")
        if len(info) > 0:
            citations = info[0].get_attribute("innerHTML").strip()

            h_index = info[2].get_attribute("innerHTML").strip()

            i10_index = info[4].get_attribute("innerHTML").strip()
        else:
            citations = 0
            h_index = 0
            i10_index = 0
        print("done citations, h_index, i10_index")
        return int(citations), int(h_index), int(i10_index)

    def _crawl_co_authors(self, driver: webdriver.Chrome, secs):
        co_authors = []

        try:
            driver.find_element(By.XPATH, "//button[@id='gsc_coauth_opn']").click()
            time.sleep(secs)

            for author in driver.find_elements(
                By.XPATH, "//div[@class='gsc_ucoar gs_scl']"
            ):
                data = {}
                user_id = author.find_element(By.TAG_NAME, "a").get_attribute("href")

                data["user_id"] = user_id[
                    user_id.find("user=") + 5  : user_id.find("user=") + 17
                ]

                data["name"] = author.find_elements(By.TAG_NAME, "a")[1].text.strip()

                data["org"] = (
                    author.find_element(By.XPATH, "//div[@class='gs_ai_aff']")
                    .get_attribute("innerHTML")
                    .strip()
                )

                co_authors.append(data)

                time.sleep(secs)
            driver.find_element(By.XPATH, "//a[@id='gsc_md_cod-x']").click()

            if co_authors == []:
                for author in driver.find_element(
                    By.XPATH, "//ul[@class='gsc_rsb_a']"
                ).find_elements(By.XPATH, "//div[@class='gsc_rsb_aa']"):
                    data = {}
                    user_id = author.find_element(By.TAG_NAME, "a").get_attribute(
                        "href"
                    )
                    data["user_id"] = user_id[
                        user_id[
                            user_id.find("user=") + 5 : user_id.find("user=") + 17
                        ]
                    ]

                    data["name"] = author.find_element(By.TAG_NAME, "a").text.strip()

                    data["org"] = (
                        author.find_element(By.XPATH, "//span[@class='gsc_rsb_a_ext']")
                        .get_attribute("innerHTML")
                        .strip()
                    )

                    co_authors.append(data)
        except:
            pass

        print("done co authors")
        return co_authors

    def _crawl_papers(self, driver: webdriver.Chrome, secs, user_id):
        papers = []

        while not driver.find_element(
            By.XPATH, "//button[@id='gsc_bpf_more']"
        ).get_property("disabled"):
            driver.find_element(By.XPATH, "//button[@id='gsc_bpf_more']").click()
            time.sleep(secs)

        links_paper = []
        for link in driver.find_element(
            By.XPATH, "//div[@id='gsc_a_tw']"
        ).find_elements(By.XPATH, "//td[@class='gsc_a_t']"):
            links_paper.append(
                link.find_element(By.TAG_NAME, "a").get_attribute("href")
            )

        links_paper = links_paper

        for index, link in enumerate(links_paper):
            try:
                driver_, _ = get_driver(no_proxy=True, headless=True)
                driver_.get(link)
                papers.append(self.crawl_paper_detail(driver_, link, user_id, index))
                print("done, {}".format(link))
                driver_.quit()
            except:
                continue

        print("done papers")
        return papers

    def _crawl_paper_detail(self, driver: webdriver.Chrome, link, user_id, index_pdf):
        data = {}

        data["user_id"] = user_id
        # ID
        data["paper_id"] = link.split(":")[-1]

        try:
            data["title"] = (
                driver.find_element(By.XPATH, "//div[@id='gsc_oci_title']")
                .find_element(By.TAG_NAME, "a")
                .get_attribute("innerHTML")
                .strip()
            )
        except:
            data["title"] = driver.find_element(
                By.XPATH, "//div[@id='gsc_oci_title']"
            ).text.strip()

        for index, el in enumerate(
            driver.find_elements(By.XPATH, "//div[@class='gsc_oci_field']")
        ):
            if (
                el.get_attribute("innerHTML") == "Authors"
                or el.get_attribute("innerHTML") == "Inventors"
            ):
                data["author_list"] = [
                    i.strip()
                    for i in driver.find_elements(
                        By.XPATH, "//div[@class='gsc_oci_value']"
                    )[index]
                    .get_attribute("innerHTML")
                    .split(",")
                ]

            # Date
            if el.get_attribute("innerHTML") == "Publication date":
                data["year"] = (
                    driver.find_elements(By.XPATH, "//div[@class='gsc_oci_value']")[
                        index
                    ]
                    .get_attribute("innerHTML")
                    .split("/")[0]
                )
                if int(data["year"]) > int(date.today().strftime("%Y")):
                    data["year"] = date.today().strftime("%Y")

            # journal
            if (
                el.get_attribute("innerHTML") == "Conference"
                or el.get_attribute("innerHTML") == "Journal"
            ):
                data["publication"] = (
                    driver.find_elements(By.XPATH, "//div[@class='gsc_oci_value']")[
                        index
                    ]
                    .get_attribute("innerHTML")
                    .strip()
                )

            # Description
            if el.get_attribute("innerHTML") == "Description":
                try:
                    data["descripton"] = (
                        driver.find_elements(By.XPATH, "//div[@class='gsc_oci_value']")[
                            index
                        ]
                        .find_element(By.XPATH, "//div[@class='gsh_csp']")
                        .get_attribute("innerHTML")
                        .strip()
                    )
                except:
                    data["descripton"] = (
                        driver.find_elements(By.XPATH, "//div[@class='gsc_oci_value']")[
                            index
                        ]
                        .find_element(By.XPATH, "//div[@class='gsh_small']")
                        .get_attribute("innerHTML")
                        .strip()
                    )

            # Citations
            if el.get_attribute("innerHTML") == "Total citations":
                data["citations"] = (
                    driver.find_elements(By.XPATH, "//div[@class='gsc_oci_value']")[
                        index
                    ]
                    .find_element(By.TAG_NAME, "a")
                    .get_attribute("innerHTML")
                    .split(" ")[-1]
                )

            # Link
            try:
                data["link"] = driver.find_element(
                    By.XPATH, "//a[@class='gsc_oci_title_link']"
                ).get_attribute("href")
            except:
                pass

            # Link pdf
            try:
                data["link_pdf"] = (
                    driver.find_element(By.XPATH, "//div[@class='gsc_oci_title_ggi']")
                    .find_element(By.TAG_NAME, "a")
                    .get_attribute("href")
                )
            except:
                pass
        return data
