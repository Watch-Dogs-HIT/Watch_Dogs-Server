#!/usr/bin/env python
# encoding:utf-8

"""字符串转json测试"""

import yaml
import json

t = """
{
	"host":"10.245.146.202",
	"pid":"32582",
	"type":"数据库",
	"comment":"MongoDB数据库"
}
"""


def byteify(input_unicode_dict, encoding='utf-8'):
    """
    将unicode字典转为str字典
    reference : https://www.jianshu.com/p/90ecc5987a18
    """
    if isinstance(input_unicode_dict, dict):
        return {byteify(key): byteify(value) for key, value in input_unicode_dict.iteritems()}
    elif isinstance(input_unicode_dict, list):
        return [byteify(element) for element in input_unicode_dict]
    elif isinstance(input_unicode_dict, unicode):
        return input_unicode_dict.encode(encoding)
    else:
        return input_unicode_dict


print byteify(json.loads(t))
# yaml 处理多行有问题
# print yaml.safe_load(t)
