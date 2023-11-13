import numpy as np
import pandas as pd
from loguru import logger
from pymongo import MongoClient, UpdateOne
import json
# from tqdm import tqdm
# from config.config import settings
from config import settings

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

    def get_data(self, query):
        """
        get data in range
        start: datetime.datetime object
        end: datetime.datetime object
        return a dataframe
        """
        data = []
        _query = query
        for dat in self.collection.find(_query):
            data.append(dat)
        return data

    # def bulk_update_or_insert(self, new_records, columns=['tradingdate']):
    #     '''
    #         Check if exist data then update else insert 
    #     '''
    #     # Loop through each new record
    #     update_operations = [
    #         UpdateOne({column: record[column] for column in columns}, {"$set": record}, upsert=True)
    #             for record in new_records
    #     ]   
    #     # Execute the bulk write operation
    #     self.collection.bulk_write(update_operations)

    def bulk_update_or_insert(self, new_records, columns=['user_id']):
        '''
            Check if exist data then update else insert 
        '''
        # Loop through each new record
        update_operations = [
            UpdateOne({column: record[column] for column in columns}, {"$set": record}, upsert=True)
                for record in new_records
        ]   
        # Execute the bulk write operation
        self.collection.bulk_write(update_operations)

if __name__=="__main__":
    db_name = 'huyanh_db'
    collection_name = 'author_test'
    mongo = MongoDB()
    mongo.set_database(db_name)
    mongo.set_collection(collection_name)

    # x = mongo.retrieve_n_last_records(1)
    # for i in x:
    #     print(i)
    with open(r'C:\Users\Admin\Documents\code\csiro-crawler\src\data\scholar\all_author.json','r',encoding='utf8') as file:
        data = json.loads(file.read())
        # print(data)
    mongo.bulk_update_or_insert(data)
    print(mongo.collection.count_documents(filter={}))
    # print(mongo.conn[db_name].list_collection_names()) 
    # mongo.set_database(db_name) 
    # mongo.set_collection(collection_name)
    # data = []
    # print(mongo.get_collection_name())
    mongo.disconnect()
    # mongo.bulk_update_or_insert(data, columns=['quarter', 'year'])

