import random
import string
import re

s1 = u'ÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚÝàáâãèéêìíòóôõùúýĂăĐđĨĩŨũƠơƯưẠạẢảẤấẦầẨẩẪẫẬậẮắẰằẲẳẴẵẶặẸẹẺẻẼẽẾếỀềỂểỄễỆệỈỉỊịỌọỎỏỐốỒồỔổỖỗỘộỚớỜờỞởỠỡỢợỤụỦủỨứỪừỬửỮữỰựỲỳỴỵỶỷỸỹ'
s0 = u'AAAAEEEIIOOOOUUYaaaaeeeiioooouuyAaDdIiUuOoUuAaAaAaAaAaAaAaAaAaAaAaAaEeEeEeEeEeEeEeEeIiIiOoOoOoOoOoOoOoOoOoOoOoOoUuUuUuUuUuUuUuYyYyYyYy'


def remove_accents(input_str):
    s = ''
    for c in input_str:
        if c in s1:
            s += s0[s1.index(c)]
        else:
            s += c
    return s


def string_to_slug(kw):
    kw = remove_accents(kw)
    data_after_process_replace = kw.lower().replace(
        " ", " ").replace("'", " ").replace("-", " ")
    data = re.sub('\s+', ' ', data_after_process_replace.strip()
                  ).replace(" ", "_")
    return data


def strip_start_end_string_dash(kw):
    data = re.sub('\s+', ' ', kw.strip())
    data = re.sub('-\s', '-', data)
    data = re.sub('\s-', '-', data)
    return data


def strip_start_end_string(kw):
    data = re.sub('\s+', ' ', kw.strip())
    return data


def random_string(length: int):
    data_random_str = ''.join(random.choice(string.ascii_uppercase + string.digits)
                              for _ in range(length))
    return data_random_str


def assign_value_in_python(initial_obj, target_obj):
    keys_in_initial_obj = initial_obj.keys()
    for each_key in keys_in_initial_obj:
        if each_key not in target_obj.keys():
            target_obj[each_key] = initial_obj[each_key]
    return target_obj
