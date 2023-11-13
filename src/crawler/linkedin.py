import time 
import json 
import os
import requests
import pandas as pd 
import ast 

from src.database.mongo import MongoDB
from src.crawler.base_crawler import BaseCrawler
from src.config.config import settings
from src.utils.bloomfilter_utils import Bloomfilter as BloomFilter
from src.config.config import settings

class LinkedinCrawler(BaseCrawler):
    def __init__(self, config, db, out_dir):
        super(BaseCrawler, self).__init__()
        self.config = config
        self.db = MongoDB()
        self.db.set_database(db_name=db)
        self.out_dir = out_dir
        self.key = settings.nubela_key
        self.saved_dir  = os.path.join(self.out_dir, "linkedin")
        if not os.path.exists(self.saved_dir):
            os.makedirs(self.saved_dir)
        self.bloom_filter = BloomFilter(self.saved_dir + '/organise_link.txt')        
        self.industries = [
            'Telecommunications',
            'IT Services and IT Consulting',
            'Software Development',
            'Computer Games',
            'E-learning',
            'Computer Networking Products',
            'Mobile Gaming Apps',
            'Technology, Information and Internet',
            'Research Services',
            'Computer and Network Security',
            'Sviluppo di software',
            'Computer Hardware Manufacturing',
            'Internet Publishing',
            'Computer Software',
            'Information Services',
            'Computer & Network Security', 
            'E-Learning Providers', 
            'Servizi IT e consulenza IT', 
            'Information Technology & Services',
            'Computers and Electronics Manufacturing', 
            'Wireless Services', 'Internet',
            'Information Technology and Services',
        ]
        self.keywords = [
            'software', 'data engineer', 'deep learning', 'big data', 'blockchain',
            '3D printing', 'Adtech', 'artificial intelligence', 'machine learning', 'augmented reality', 
            'sensor', 'autonomous vehicle', 'car sharing', 'cloud computing', 'cryptocurrency', 
            'cybersecurity', 'e-commerce', 'EdTech', 'digital health', 'smart health', 
            'FinTech', 'Internet of Things', 'IoT', 'robotics', 'drones', 'SaaS', 
            'SpaceTech', 'TMT', 'virtual reality', 'wearables', 'smart home', 'smart grid', 
            'digital twin', 'edge computing', 'quantum', 'IoT security', 'communication and networking', 
            'telecommunication', 'data processing'
        ]
        self.country = self.config.country

    def update_existed_companies(self, mode_save):
        existed_links = self._get_existed_links()
        lst_res = []
        for link in existed_links:
            res_comp, _ = self._crawl_all_info_company(link)
            if mode_save in ['db', 'all']:
                query = {
                    
                }
                self._update_existed_companies_in_db(query, lst_res)
            elif mode_save in ['local', 'all']:
                self._save_data(res_comp, self.saved_dir, mode_save)

    def crawl_new_companies(self):
        new_company_urls = self._get_new_companies()
        lst_res =  []

        for link in new_company_urls:
            res = self._crawl_all_info_company(link)
            lst_res.append(res)
        return lst_res
    
    def _clean_company(self, input_data, linkedin_link):
        
        it = {}
        country_2_code = {
            'vietnam': 'VN',
            'australia': 'AU'
        }
        

        is_in_region = False
        try:
            it['name'] = input_data['name']
            it['link'] = linkedin_link
            for loc in input_data['locations']:
                if loc['country'] == country_2_code[self.config.country]:
                    if not loc['line_1']:
                        loc['line_1'] = ''
                    if not loc['city']:
                        loc['city'] = ''
                    if not loc['state']:
                        loc['state'] = ''
                    it['address'] = loc['line_1'] + ', ' + loc['city'] + ', ' + loc['state'] + ', ' + 'Australia'
                    it['postcode'] = loc['postal_code']
                    is_in_region = True
                    break
            it['phone_number'] = ''
            it['founded_year'] =  input_data['founded_year']
            it['summary_description'] = input_data['description']
            if not input_data['company_size'][0]:
                input_data['company_size'][0] = 0
            if not input_data['company_size'][1]:
                input_data['company_size'][1] = 0 
            it['nums_employee'] = str(input_data['company_size'][0]) + '-' + str(input_data['company_size'][1])
            it['website'] = input_data['website']
            try:
                it['technology'] =  input_data['specialities'] if len(input_data['specialities']) > 1 else input_data['specialities'][0]
            except:
                it['technology'] = ''
            it['industry_focus'] = input_data['industry']
            it['similar_companies']= input_data['similar_companies']
            it['company_id'] = ''
            if not is_in_region:
                return {}
        except:
            return {}
        return it 

    def _get_existed_links(self):
        return self.bloom_filter.items
    
    def _get_new_companies(self):
        posts = self._crawl_posts()
        try:
            post_similars = self._crawl_similar_posts(posts)
        except:
            post_similars = pd.DataFrame(columns=['name','link','industry','location'])
        posts_final = pd.concat([posts, post_similars])
        posts_final = posts_final[~(posts_final['location'].isna()) & (posts_final['industry'].isin(self.industries))].reset_index(drop=True)
        lst_job_urls = posts_final['link'] 
        unique_lst_job_urls = list(set(lst_job_urls))
        existed_urls = self._get_existed_links()
        return [link for link in unique_lst_job_urls if link not in existed_urls]

    def _crawl_similar_posts(self,data=None):
        print("Crawling similar post!")
        if data is not None: 
            df_company_infos = data
        else:
            df_company_infos = pd.read_csv(self.saved_dir + '/company_info.csv')
        existed_links = df_company_infos['link'].tolist()
        lst_similars = []
        similars = pd.DataFrame(data=df_company_infos)['similar_companies'].tolist()
        for similar in similars:
            similar =  ast.literal_eval(similar)
            lst_similars += similar
        df_sims = pd.DataFrame(data=lst_similars).drop_duplicates(subset=['name','link']).fillna('')
        
        df_sims.to_csv(self.saved_dir + '/similar_posts.csv')
        comp_links = df_sims['link'].tolist()
        comp_links = list(set(comp_links).difference(set(existed_links)))

        its = [] 
        for link in comp_links:
            try:
                if link == '' or not link:
                    continue
                comp_info = self._clean_company(self._crawl_info_company(link), link)
                if comp_info:
                    its.append(comp_info)
            except:
                pass 
        try:
            df_similar_infos =  pd.DataFrame(data=its)
        except:
            import pdb; pdb.set_trace()
        df_similar_infos.to_csv(self.saved_dir + '/similar_company_info.csv')
        return df_similar_infos
        
    def _crawl_posts(self):
        '''
            Get all company in specific region
        '''
        print("Crawling post!")
        lst_jobs = [] 
        try:
            df_jobs= pd.read_csv(self.saved_dir + '/company_posts.csv')
            lst_jobs = df_jobs.to_dict(orient='records')
        except:
            pass 
        country_2_code = {
            'vietnam': '104195383',
            'australia': '101452733'
        }
        for kw in self.keywords:
            print(kw)
            api_endpoint = 'https://nubela.co/proxycurl/api/v2/linkedin/company/job'
            api_key = self.key
            header_dic = {'Authorization': 'Bearer ' + api_key}
            params = {
                'geo_id': country_2_code[self.config.country],
                'keyword': kw
            }
            response = requests.get(api_endpoint,
                                params=params,
                                headers=header_dic)
            lst_jobs += response.json()['job']
            next_page_url = response.json()['next_page_api_url']
            i = 0
            while next_page_url and i < 25:
                try:
                    response = requests.get(next_page_url,
                                            headers=header_dic)
                    lst_jobs += response.json()['job']
                    i +=1
                    if not response.json()['next_page_api_url']:
                        break
                except:
                    break
        df_jobs =  pd.DataFrame(data=lst_jobs).drop_duplicates(subset=['company_url'])[['company', 'company_url']]
        df_jobs.to_csv(self.saved_dir + '/company_posts.csv')
        return df_jobs

    def _crawl_all_info_company(self):
        datas = []
        df_posts = pd.read_csv(self.saved_dir + '/company_posts.csv').rename(columns={"company":'name', 'company_url':'link'})
        df_posts = df_posts[['name', 'link']]
        try:
            df_similars= pd.read_csv(self.saved_dir + '/similar_posts.csv')[['name', 'link']]
            df_final =  pd.concat([df_posts, df_similars]).drop_duplicates(subset=['name', 'link'])
        except:
            df_final = df_posts
        urls = df_final['link'].tolist()
        datas = []
        
        for link in urls:
            data_raw = self._crawl_info_company(link)
            data = self._clean_company(data_raw,link)
            if data:
                datas.append(data)
        # up to db 
        df_info = pd.DataFrame(datas)
        df_info.to_csv(self.saved_dir + '/company_info.csv')
        return df_info

    def _crawl_info_company(self, url):
        print("Crawling company: " + str(url))
        api_key = self.key
        api_endpoint = 'https://nubela.co/proxycurl/api/linkedin/company'
        header_dic = {'Authorization': 'Bearer ' + api_key}
        params = {
            'url': url,
        }
        response = requests.get(api_endpoint,
                                params=params,
                                headers=header_dic)
        return response.json()

    def _filter_by_keywords(self):
        df_companies = pd.read_csv(self.saved_dir + '/company_info.csv')
        df_companies_similars= pd.read_csv(self.saved_dir + '/similar_company_info.csv')
        df_final =  pd.concat([df_companies, df_companies_similars]).drop_duplicates(subset=['name', 'link'])
        df_in_industry_ict = df_final[df_final['industry_focus'].isin(self.industries)][['name','link','address','postcode','phone_number','founded_year','summary_description','nums_employee','website','technology','industry_focus','similar_companies','company_id']]
        df_not_in_industry_ict = df_final[~df_final['industry_focus'].isin(self.industries)][['name','link','address','postcode','phone_number','founded_year','summary_description','nums_employee','website','technology','industry_focus','similar_companies','company_id']]
        df_in_industry_ict.to_csv(self.saved_dir + '/comp_in_ict.csv')
        df_not_in_industry_ict.to_csv(self.saved_dir + '/comp_not_in_ict.csv')
        return df_in_industry_ict, df_not_in_industry_ict

