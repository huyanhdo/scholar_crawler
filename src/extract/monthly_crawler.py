import os
import random
import time
from datetime import datetime
from loguru import logger
from datetime import datetime
import pandas as pd


from src.config.config import settings
from src.crawler.linkedin import LinkedinCrawler
from src.crawler.clutch import ClutchCrawler 
from src.crawler.wipo import WipoCrawler 
from src.database.mongo import MongoDB

class MonthlyCrawler:
    def __init__(self, save_path, mode, mode_save, country) -> None:
        self.config = settings
        self.config.country = country
        self.save_path = save_path
        self.mode = mode 
        self.output_dir = os.path.join(self.save_path, mode)
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        self.linkedin_crawler = LinkedinCrawler(config=self.config, db=self.config.database_linkedin, out_dir=self.output_dir)
        self.clutch_crawler = ClutchCrawler(config=self.config, db=self.config.database_clutch, out_dir=self.output_dir)
        self.wipo_crawler = WipoCrawler(config=self.config,db=self.config.database_wipo, out_dir=self.output_dir)
        self.mode_save = mode_save

    def batch_monthly_crawler(self, crawl_new, update):
        if update:
            self.linkedin_crawler.update_existed_companies(mode_save=self.mode_save)
            self.clutch_crawler.update_existed_companies(mode_save=self.mode_save)
            # self.wipo_crawler.update_existed_companies(mode_save=self.mode_save)
        if crawl_new:
            # check from list and crawl non-existed
            # self.linkedin_crawler.crawl_new_companies(mode_save=self.mode_save)
            self.clutch_crawler.crawl_new_companies(mode_save=self.mode_save)
            # self.wipo_crawler.crawl_new_companies(mode_save=self.mode_save)
        if not update and not crawl_new:
            print("No action between crawl_new/update is chosen.")