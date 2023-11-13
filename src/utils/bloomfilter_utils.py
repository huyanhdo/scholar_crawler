from pybloom import BloomFilter
from ast import literal_eval
import os 
class Bloomfilter:
    def __init__(self, save_file) -> None:
        try:
            with open(save_file, "r+") as f:
                # lst_file = [list(literal_eval(line)) for line in f]
                lst_file = f.read().split('\n')
        except:
            lst_file = []
        self.save_file = save_file
        # print(save_file)
        self._items = lst_file
        self.f = BloomFilter(capacity=100000, error_rate=0.001)
        for item in self._items:
            self.f.add(item)

    @property 
    def items(self):
        return self.f

    def add_new_items(self, item):
        self._items += [item]
        self.f.add(item)

    def check_item_exist(self,item):
        if item in self.f:
            return True
        return False 

    def save(self):
        with open(self.save_file,'w',encoding='utf8') as f:
            # f.writelines(self._items)
            # print(self._items)
            # print(type(self._items))
            for item in self._items:
                f.write(item+'\n')