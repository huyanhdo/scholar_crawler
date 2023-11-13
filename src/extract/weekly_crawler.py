import os
import random
import time
from datetime import datetime
from datetime import datetime
import pandas as pd

from src.config.config import settings
from src.crawler.scholar import GgscholarCrawler 

class WeeklyCrawler:
    def __init__(self, save_path, mode) -> None:
        self.config = settings
        self.save_path = save_path
        self.mode = mode 
        self.output_dir = os.path.join(self.save_path, mode)
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        self.scholar_crawler = GgscholarCrawler(db=self.config.database_scholar)

    def batch_weekly_crawler(self, crawl_new, update):
        if update:
            self.scholar_crawler.update_existed_authors()
            self.scholar_crawler.update_existed_organizations() 
        if crawl_new:
            # check from list organization and list author 
            self.scholar_crawler.crawl_new_authors()
            self.scholar_crawler.crawl_new_organizations()

