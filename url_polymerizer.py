# -*- coding: utf-8 -*-

import sys, re, urlparse

########## URL聚合 #########
def polymerize(url, parseQuery):
    url = url.strip(' "\'\r\n\t')
    if not url: return 
    if re.search(r'\.(?:js|css|ico|png|jpg)', url): return

    info = urlparse.urlparse(url)
    if not info.hostname: return

    keysPath, keysQuery = [], [] 
    keys = re.split(r'/|-', info.path)
    for i in range(len(keys)):
        k = keys[i]
        v = '' if i == len(keys) - 1 else keys[i+1]

        if dropPair(k, v, url): i += 1; continue;
        if dropItem(k): continue
        keysPath.append(k)
    if len(keysPath) > 6: keysPath = keysPath[0:6]

    if parseQuery:
        kvs = urlparse.parse_qsl(info.query)
        for kv in kvs:
            if not kv: continue
            if dropPair(kv[0], kv[1], info.path) or dropItem(kv[0]): continue;
            kvStr = '%s=%s' % (kv[0], valueAbstract(kv[1]))
            keysQuery.append(kvStr)
    pickNum = min(6, 8 - len(keysPath))
    if len(keysQuery) > pickNum: keysQuery = keysQuery[0:pickNum]
    keysQuery.sort()

    hostname = info.hostname.replace('51fanli', 'fanli')
    path = '/'.join(keysPath).strip('/')
    query = '&'.join(keysQuery).strip('&')

    urlCode = "%s/%s?%s" % (hostname, path, query)
    return urlCode.strip(' /?')

def valueAbstract(value):
    if re.search(r'^[\d,;]+$', value): return '%d'
    return '%s'

def dropPair(k, v, path= ''):
    drop = False
    k = k.lower()
    drop = drop or (type(v) != str)
    drop = drop or len(v) == 0 or len(v) > 24
    drop = drop or re.search(r'^(?:c_)?nt$', k) and re.search(r'^(?:wifi|cell)$', v)
    drop = drop or k in ['jsoncallback', 'spm', 'lc', '_t_t_t', 't', '_t', '__', '_', 'abtest']
    drop = drop or k in ['size', 'psize', 'page_size', 'pagesize', 'psize', 'page', 'pidx', 'p', 't'] and re.search(r'^[\d-]*$', v)
    drop = drop or ('size' == k and (v in ['small', 'big']))
    drop = drop or re.search(r'^a?sort$', k) and re.search(r'sort|default|asc|des', v, re.IGNORECASE)
    drop = drop or k in ['verify_code', 'app_ref', 'deviceno', 'device_no', 'deviceid', 'devid', 'msg', 'security_id'] and re.search(r'^\w{12,}', v)
    drop = drop or re.search(r'(start|end)_price', k) and v.isdigit()
    drop = drop or re.search(r'time', k) and re.search(r'\d{10}|0', v)
    drop = drop or k in ['ajax'] and v.isdigit()
    drop = drop or re.search(r'https?://', v)
    drop = drop or re.search(r'^(start|offset|limit)$', k) and re.search(r'search', path)
    drop = drop or re.search(r'^utm_.*$', k) and len(v) > 12

    return drop

def dropItem(k):
    drop = False
    k = k.lower()
    if (re.search(r'\.(php5?|htm|html5?|do|jsp|asp)$', k)):
        return False

    drop = drop or not re.search(r'^[a-zA-Z_]\w{1,24}$', k)
    drop = drop or re.search(r'^c_(?:src|v|nt|aver)$', k)
    drop = drop or re.search(r'^\w+_(?:asc|desc)$', k)
    #http://zhide.fanli.com/p{N}分页参数
    drop = drop or re.search(r'^p\d+$', k)
    if drop: return drop

    # 数字字母混杂
    numTimes = re.findall(r'(\d+)', k)
    numCount = sum(c.isdigit() for c in k)
    numRate = numCount/len(k)
    #16进制字符串数字比例一般为0.625 上下浮动0.05
    drop = drop or (len(numTimes) >= 2 and numRate >= .575 and numRate <= .675)

    return drop


########## 身份信息提取 ##########
def identity_picker(path, ip, utmo):
    pass
