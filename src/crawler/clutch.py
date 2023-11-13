import time 
import json 
import os
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (NoSuchElementException, StaleElementReferenceException)
import random

from src.database.mongo import MongoDB
from src.utils.bloomfilter_utils import Bloomfilter as BloomFilter
from src.utils.selenium_utils import get_driver, clean, hashing 
from src.crawler.base_crawler import BaseCrawler

class ClutchCrawler(BaseCrawler):
    def __init__(self, config, db, out_dir):
        super( BaseCrawler,self).__init__()
        self.config=config
        self.db = MongoDB()
        self.db.set_database(db_name=db)
        self.base_url = 'https://clutch.co/'
        self.out_dir = out_dir
        self.saved_link  = os.path.join(self.out_dir,"clutch")
        if not os.path.exists(self.saved_link):
            os.makedirs(self.saved_link)
        self.bloom_filter = BloomFilter(self.saved_link + '/organise_link.txt')
        self.driver = get_driver(headless=False) 

    def update_existed_companies(self, mode_save):
        existed_links = self._get_existed_links()
        lst_res = []
        for link in existed_links:
            driver = get_driver(headless=True)
            res_comp, _ = self._crawl_all_info_company(driver=driver, url=link)
            # lst_res.append(res_comp)
            if mode_save in ['db', 'all']:
                query = {

                }
                self._update_existed_companies_in_db(query, lst_res)
            elif mode_save in ['local', 'all']:
                self._save_data(res_comp, self.out_dir, mode_save)

    def crawl_new_companies(self, mode_save):
        new_companies_links = self._get_new_links()
        lst_res = []
        for link in new_companies_links:
            res_comp, _ = self._crawl_all_info_company(url=link)
            # lst_res.append(res_comp)
            if mode_save in ['db', 'all']:
                self._save_new_companies_in_db(lst_res)
            elif mode_save in ['local', 'all']:
                self._save_data(res_comp, self.saved_link)
    
    def _get_existed_links(self):
        return self.bloom_filter.items
    
    def _get_new_links(self):
        
        links = self._crawl_link()
        existed_links = self._get_existed_links()
        return [link for link in links if link not in existed_links]
    
    def _crawl_link(self):
        links = []

        country_2_code = {
            'vietnam': 'vn',
            'australia': 'au'
        }    

        categories = {
            'Mobile App Development': '/app-developers',
            'Web Developers': '/web-developers',
            'Software Developers': '/developers',
            'AR/VR': '/developers/virtual-reality',
            'Artificial Intelligence': '/developers/artificial-intelligence',
            'Blockchain': '/developers/blockchain'
        }

        for cat in categories.keys():
            url = self.base_url + country_2_code[self.config.country] +categories[cat]
            self.driver.get(url) 
            comp_info = "//h3[@class='company_info']"

            page_nums = 1
            try:
                page_nums = len(self.driver.find_element(
                    By.XPATH, "//nav[@aria-label='Page navigation']").find_elements(By.TAG_NAME, 'li')) - 2
            except:
                pass

            for i in range(page_nums):
                self.driver.get('{}?page={}'.format(url, i))
                time.sleep(random.randint(1,5))
                for company_link in self.driver.find_elements(
                        By.XPATH, comp_info):
                    link = company_link.find_element(By.TAG_NAME, 'a').get_attribute('href')
                    if 'profile' in link:
                        links.append(link)
        return list(set(links))

    def _crawl_all_info_company(self, url):
        result = {}
        self.driver.get(url)

        result.update({'link': url})
        result.update(self._crawl_name())
        org_id = hashing(result['name'])
        result.update({'org_id': org_id})
        result.update(self._crawl_website())
        result.update(self._crawl_logo())
        result.update(self._crawl_location())
        result.update(self._crawl_summary())
        result.update(self._crawl_contact())
        result.update(self._crawl_service_focus())
        result.update(self._crawl_porfolio())
        result.update(self._crawl_id())

        reviews = {}
        try:
            reviews = self._crawl_reviews(id=org_id, url=url, name=result['name'])
        except:
            pass
        return result, reviews

    def _crawl_name(self):
        name = ''
        try:
            name = clean(self.driver.find_element(
                By.XPATH, "//h1[@class='header-company--title' or @class='header-company--title small']").get_attribute('innerHTML'))
        except Exception as e:
            print('crawl name', e)
        return {
            'name': name
        }

    def _crawl_website(self):
        website = ''
        try:
            website = clean(self.driver.find_element(
                By.XPATH, "//h1[@class='header-company--title' or @class='header-company--title small']").find_element(By.TAG_NAME, 'a').get_attribute('href'))
        except Exception as e:
            print('crawl website', e)
        return {
            'website': website
        }

    def _crawl_logo(self):
        logo = ''
        try:
            logo = clean(self.driver.find_element(
                By.XPATH, '//div[@class="header-company company_logotype"]').find_element(By.TAG_NAME, 'img').get_attribute('src'))
        except Exception as e:
            print('crawl logo', e)

        return {
            'logo': logo
        }

    def _crawl_location(self):
        locations = []
        temp = self.driver.find_element(By.XPATH, '//button[@id="showAllLocation"]')
        self.driver.execute_script("arguments[0].click();", temp)

        for el in self.driver.find_elements(By.XPATH, '//div[@class="address"]'):
            content = clean(el.get_attribute('innerHTML'))
            string_temp = content.split(' ')
            location = ''
            phone_number = ''
            for index, i in enumerate(string_temp):
                location = content
                if '84' in i:
                    location = ' '.join(string_temp[:index])
                    phone_number = ' '.join(string_temp[index:])
                    break
            locations.append({
                'location': location,
                'phone_number': phone_number})

        return {
            'locations': locations
        }

    def _crawl_summary(self):
        summary_el = self.driver.find_element(
            By.XPATH, "//div[@class='col-md-6 summary-description']")
        agg_rating = None
        total_rating = None
        description = None
        verification_status = None
        min_project_size = None
        hourly_rate = None
        nums_employee = None
        founded_year = None
        languages = None

        # agg_rating
        try:
            agg_rating = clean(summary_el.find_element(
                By.XPATH, "//span[@class='rating sg-rating__number']").get_attribute('innerHTML'))
        except Exception as e:
            print('crawl agg rating', e)

        # total_rating
        try:
            total_rating = clean(summary_el.find_element(
                By.XPATH, "//a[@class='reviews-link sg-rating__reviews']").get_attribute('innerHTML'))
        except Exception as e:
            print('crawl total rating', e)

        # description
        try:
            description = clean(summary_el.find_element(
                By.ID, 'summary_description').get_attribute('innerHTML'))
        except Exception as e:
            print('crawl des', e)

        # vertification status
        try:
            verification_status = clean(
                summary_el.find_element(By.XPATH, "//div[@class='verification-status-wrapper']").get_attribute('innerHTML'))
        except Exception as e:
            print('crawl vertification', e)

        # min_project_size
        try:
            min_project_size = clean(summary_el.find_element(
                By.XPATH, "//div[@data-content='<i>Min. project size</i>']").get_attribute('innerHTML'))
        except Exception as e:
            print('crawl min project size', e)

        # hourly_rate
        try:
            hourly_rate = clean(summary_el
                                .find_element(By.XPATH, "//div[@data-content='<i>Avg. hourly rate</i>']").get_attribute('innerHTML'))
        except Exception as e:
            print('crawl hourly rate', e)

        # nums_employee
        try:
            nums_employee = clean(summary_el
                                .find_element(By.XPATH, "//div[@data-content='<i>Employees</i>']").get_attribute('innerHTML'))
        except Exception as e:
            print('crawl nums_employee', e)

        # founded_year
        try:
            founded_year = clean(summary_el
                                .find_element(By.XPATH, "//div[@data-content='<i>Founded</i>']").get_attribute('innerHTML'))
        except Exception as e:
            print('crawl founded_year', e)

        # languages
        try:
            languages = clean(summary_el
                            .find_element(By.XPATH, "//div[@class='summary-popup language']").find_element(By.XPATH, "//ul[@class='summary-popup--list']").get_attribute('innerHTML')).split()
        except Exception as e:
            print('crawl languages', e)

        return {
            'summary_description': {
                'agg_rating': agg_rating,
                'total_rating': total_rating,
                'description': description,
                'verification_status': verification_status,
                'min_project_size': min_project_size,
                'hourly_rate': hourly_rate,
                'nums_employee': nums_employee,
                'founded_year': founded_year,
                'languages': languages
            }
        }

    def _crawl_contact(self):
        phone_number = None
        contact_link = []

        quick_menu_el = self.driver.find_element(By.ID, "quick-menu")
        try:
            phone_number = clean(quick_menu_el.find_element(
                By.XPATH, "//a[@class='contact phone_icon']").get_attribute('innerHTML'))
        except Exception as e:
            print('crawl phone number', e)

        try:
            for el in quick_menu_el.find_element(By.XPATH, "//li[@class='profile-social-wrap']").find_elements(By.TAG_NAME, 'a'):
                contact_link.append(el.get_attribute('href'))
        except Exception as e:
            print('crawl contact link', e)

        return {
            'contact': {
                'phone_number': phone_number,
                'link': contact_link
            }
        }

    def _crawl_service_focus(self):
        result = {}
        els = self.driver.find_elements(By.XPATH, "//div[@class='graph-title']")

        for index, title_el in enumerate(els):
            list_el = self.driver.find_elements(
                By.XPATH, "//div[@class='chartAreaContainer spm-bar-chart']")[index]
            list_service = {}
            names = []
            percentages = []
            for service_el in list_el.find_elements(
                    By.TAG_NAME, "div"):
                name_service = clean(service_el.get_attribute('data-content'))
                percentage = clean(service_el.get_attribute('innerHTML'))
                if percentage in name_service:
                    name_service = name_service.replace(percentage, '')
                names.append(name_service)
                percentages.append(percentage)
            list_service['name'] = names
            list_service['percentage'] = percentages

            title_name = clean(title_el.get_attribute(
                'innerHTML')).lower().replace(' ', '_')
            result[title_name] = list_service

        return {
            'service_focus': result
        }

    def _crawl_porfolio(self):
        clients = None
        projects = []

        try:
            porfolio_el = self.driver.find_element(By.ID, "portfolio")
            clients = clean(porfolio_el.find_element(
                By.XPATH, "//div[@class='field field-name-clients']").get_attribute('innerHTML'))
        except Exception as e:
            print('crawl portfolio', e)

        try:
            for project_el in self.driver.find_element(By.ID, "project-preview-wrapper").find_elements(By.XPATH, "//div[@class='p-element']"):
                result = {}
                result['img'] = project_el.find_element(
                    By.TAG_NAME, 'img').get_attribute('data-src')
                result['name'] = clean(
                    project_el.find_element(By.CLASS_NAME, 'item-title').get_attribute('innerHTML'))
                projects.append(result)
        except Exception as e:
            print('crawl projects', e)

        return {
            'porfolio': {'clients': clients,
                        'projects': projects}
        }

    def _crawl_reviews(self, id, url, name):
        reviews_el = self.driver.find_element(By.XPATH, "//section[@id='reviews']")
        reviews = []
        temp = self.driver.find_element(By.XPATH, '//a[@href="#reviews"]')
        self.driver.execute_script("arguments[0].click();", temp)
        self.driver.find_element(By.XPATH, '//a[@href="#reviews"]').click()
        time.sleep(2)

        try:
            if self.driver.find_element(
                    By.XPATH, "//ul[@class='pagination']"):
                pagination_el = self.driver.find_element(
                    By.XPATH, "//ul[@class='pagination']").find_elements(By.TAG_NAME, 'li')

                pagination_el = pagination_el[:len(pagination_el) - 2]

                for index, page_el in enumerate(pagination_el):
                    time.sleep(5)
                    try:
                        for idx, review in enumerate(reviews_el.find_elements(
                                By.XPATH, '//div[@class="feedback client-interview"]')):
                            id_review = review.get_attribute('id')
                            project_review = {}
                            review_content = {}
                            reviewer = {}

                            project_review = self._crawl_project_review(
                                review_el=review, id_review=id_review, idx=idx, paging=True)
                            review_content = self._crawl_review_content(
                                review, id_review, idx, paging=True)
                            reviewer = self._crawl_reviewer(
                                review, id_review, idx, paging=True)

                            reviews.append(
                                {'org_id': id,
                                'name': name,
                                'link': url,
                                'id': id_review,
                                'project_review': project_review,
                                'review': review_content,
                                'reviewer': reviewer})
                        # print('Done page {}'.format(index + 1))
                        if (index + 1 == len(pagination_el)):
                            break
                        self.driver.find_element(
                            By.XPATH, "//li[@class='page-item next']").click()
                    except Exception as e:
                        print('crawl review', e)
                        continue
        except:
            for idx, review in enumerate(reviews_el.find_elements(
                    By.XPATH, '//div[@class="feedback client-interview"]')):
                id_review = review.get_attribute('id')
                project_review = {}
                review_content = {}
                reviewer = {}

                project_review = self._crawl_project_review(
                    review_el=review, id_review=id_review, idx=idx)
                review_content = self._crawl_review_content(
                    review, id_review, idx)
                reviewer = self._crawl_reviewer(review, id_review, idx)
                reviews.append(
                    {'org_id': id,
                        'name': name,
                        'link': url,
                        'id': id_review,
                        'project_review': project_review,
                        'review': review_content,
                        'reviewer': reviewer})
        return {
            'id': id,
            'reviews': reviews
        }

    def _crawl_project_review(self, review_el, id_review, idx, paging=False):
        # project_review
        project_review = {}
        if paging:
            idx = idx + 1
        try:
            project_review['name'] = clean(review_el.find_element(
                By.XPATH, "//a[@href='#{}']".format(id_review)).get_attribute('innerHTML'))
            project_review['category'] = clean(review_el.find_elements(
                By.XPATH, "//div[@data-content='<i>Project category</i>']")[2 * idx].get_attribute('innerHTML'))
            project_review['size'] = clean(review_el.find_elements(
                By.XPATH, "//div[@data-content='<i>Project size</i>']")[2 * idx].get_attribute('innerHTML'))
            project_review['length'] = clean(review_el.find_elements(
                By.XPATH, "//div[@data-content='<i>Project length</i>']")[2 * idx].get_attribute('innerHTML'))
            project_review['summary'] = clean(review_el.find_elements(
                By.XPATH, "//div[@class='field field-name-proj-description field-inline']")[idx].get_attribute('innerHTML'))
        except Exception as e:
            print('crawl project review', e)

        return project_review

    def _crawl_id(self):
        try:
            xpath_id = '//*[@id="verification"]/div/div[2]/div/div/div/div/div[3]/div[1]/div/div[4]/div[2]'
            id = self.driver.find_element(By.XPATH, xpath_id).get_attribute('innerHTML')
        except:
            return {"company_id": ''}
        return {"company_id": clean(id)}

    def _crawl_review_content(self, review_el, idx, paging=False):
        # review_content
        review_content = {}
        if paging:
            idx = idx + 1
        try:
            review_content['review'] = clean(review_el.find_elements(
                By.XPATH, "//div[@class='field field-name-client-quote field-inline']")[2 * idx].get_attribute('innerHTML'))
            review_content['date'] = clean(review_el.find_elements(
                By.XPATH, "//h5[@class='h5_title date']")[idx].get_attribute('innerHTML'))
            review_content['score_rating'] = clean(review_el.find_elements(
                By.XPATH, "//span[@class='rating sg-rating__number']")[2 * (idx + 1)].get_attribute('innerHTML'))
            # group-feedback
            fb_el = review_el.find_elements(
                By.XPATH, "//div[@class='group-feedback']")[idx]
            score_list = [clean(i.get_attribute('innerHTML')) for i in fb_el.find_elements(
                By.TAG_NAME, "div")][2:]
            review_content['score_list'] = [
                i for index, i in enumerate(score_list) if index % 3 == 0]
            review_content['summary'] = clean(review_el.find_elements(
                By.XPATH, "//div[@class='field field-name-comments field-inline']")[idx].get_attribute('innerHTML'))
        except Exception as e:
            print('crawl review content', e)
        return review_content

    def _crawl_reviewer(self, review_el, idx, paging=False):
        # reviewer
        reviewer = {'title': '',
                    'name': '',
                    'org_industry': '',
                    'org_size': ''}
        if paging:
            idx = idx + 1
        # reviewer['content'] = clean(review_el.get_attribute('innerHTML'))
        # print(len(review_el.find_elements(
        #     By.XPATH, "//div[@data-content='<i>Location</i>']")))
        try:
            # print(len(review_el.find_elements(
            #     By.XPATH, "//div[@class='field-name-full-name-display']")))
            reviewer['title'] = clean(review_el.find_elements(
                By.XPATH, "//div[@class='field-name-title']")[2 * idx].get_attribute('innerHTML'))
        except Exception as e:
            print('crawl reviewer title', e)
        try:
            reviewer['name'] = clean(review_el.find_elements(
                By.XPATH, "//div[@class='field-name-full-name-display']")[2 * idx].get_attribute('innerHTML'))
        except Exception as e:
            print('crawl reviewer name', e)
        try:
            reviewer['org_industry'] = clean(review_el.find_elements(
                By.XPATH, "//div[@data-content='<i>Industry</i>']")[idx].get_attribute('innerHTML'))
        except Exception as e:
            print('crawl reviewer industry', e)
        try:
            reviewer['org_size'] = clean(review_el.find_elements(
                By.XPATH, "//div[@data-content='<i>Client size</i>']")[2 * idx].get_attribute('innerHTML'))
        except Exception as e:
            print('crawl reviewer size', e)
        # try:
        #     reviewer['org_location'] = clean(review_el.find_elements(
        #         By.XPATH, "//div[@data-content='<i>Location</i>']")[2 * idx].get_attribute('innerHTML'))
        # except Exception as e:
        #     print('crawl reviewer location', e)

        return reviewer
