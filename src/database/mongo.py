import numpy as np
import pandas as pd
from loguru import logger
from pymongo import MongoClient, UpdateOne

# from config.config import settings
from src.config.config import settings

class MongoDB:
    def __init__(self) -> None:
        mongo_uri = f"""mongodb://{settings.mongodb_username}:{settings.mongodb_password}@{settings.mongodb_host}:{settings.mongodb_port}"""
        self.conn = MongoClient(mongo_uri)
        self.database = None
        self.collection = None

    def set_database(self, db_name):
        self.database = self.conn[db_name]
        # return self.database

    def set_collection(self, col_name):
        self.collection = self.database[col_name]
        # return self.collection

    def insert_many(self, data):
        self.collection.insert_many(data)

    def update_many(self, query, data):
        self.collection.update_many(query, data)

    def disconnect(self):
        self.conn.close()

    def drop(self, col_name):
        self.database.drop_collection(col_name)

    def last_record(self, is_finan_report=False):
        last_record = self.collection.find_one({}, sort=[("_id", -1)])
        return last_record

    def retrieve_n_last_records(self, n):
        records = self.collection.find().sort("_id", -1).limit(n)
        return records

    def get_collection_name(self):
        return self.database.list_collection_names

    def get_all_data(self):
        """
        get data in range
        return a dataframe
        """
        data = []
        for dat in self.collection.find():
            data.append(dat)
        data = sorted(data, key=lambda d: d["_id"])
        data = data.drop(["_id"], axis=1)
        return data


    def bulk_update_or_insert(self, new_records, columns=['user_id']):
        '''
            Check if exist data then update else insert 
        '''
        # Loop through each new record

        new_records = list(new_records)
        
        # queries all record which have the modified field
        modified_records = self.collection.find({'modified':{'$exists':True}},{'user_id':1,'modified':1})
        
        #matching user id and delete existed fields in modified
        for item in modified_records:
            # modified_record = [x for x in new_records if x['user_id'] == item['user_id']]
            modified_record = next((x for x in new_records if x['user_id'] == item['user_id']) , None)
            
            if modified_record == None:
                continue

            for col in item['modified']:
                del modified_record[col]

        #update
        update_operations = [
            UpdateOne({column: record[column] for column in columns}, {"$set": record}, upsert=True)
                for record in new_records
        ]   

        self.collection.bulk_write(update_operations)