import json 
import os 

from src.database.mongo import MongoDB
from src.utils.selenium_utils import get_driver, clean, hashing 

class BaseCrawler:
    def __init__(self, db, out_dir) -> None:
        self.db = MongoDB()
        self.db.set_database(db_name=db)
        self.out_dir = out_dir

    def _get_existed_links(self):
        pass 
    
    def _get_new_links(self):
        pass 

    def _save_data(self, data, out_dir):
        out_file =  out_dir + '/organisation_data.json'
        if not os.path.exists(out_file):
            with open(out_file, 'w+') as f:
                json.dump(data, f)
        else:
            with open(out_file, 'a+') as f:
                json.dump(data,f)
                
    def _update_existed_companies_in_db(self, collection, data, query):
        self.db.set_collection(collection)
        self.db.update_many(query, data) 

    def _save_new_companies_in_db(self, collection, data):
        self.db.set_collection(collection)
        self.db.insert_many(data) 
