import json
import os
import re
import requests
import sys


def http_get_request(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache"
    }
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        return False
    return resp


# 获取本机公网ip地址
# 使用ipaddress.com获取快速访问ip不需要使用该函数
def get_public_IP():
    # 通过访问 http://pv.sohu.com/cityjson 来获取
    # 接口返回：{"cip": "111.196.240.67", "cid": "110000", "cname": "北京市"};
    r = http_get_request('http://pv.sohu.com/cityjson')
    start_index = r.text.find('{', 0, len(r.text))
    end_index = r.text.rfind('}', 0, len(r.text)) + 1
    if start_index >= 0 and end_index >= 0:
        result = json.loads(r.text[start_index:end_index])
    else:
        result = {}
    return result.get('cip')


def get_IP_address_of_domain(domain, myip=None):
    primary_domain = domain
    domain_part = primary_domain.split('.')
    if len(domain_part) > 2:
        primary_domain = '.'.join(domain_part[-2:])
    if primary_domain == domain:
        url = "https://" + primary_domain + ".ipaddress.com/"
    else:
        url = "https://" + primary_domain + ".ipaddress.com/" + domain
    data = http_get_request(url)
    if not data:
        return
    else:
        data = data.text
    re_compile = r'<a href=\"https://www.ipaddress.com/ipv4/([\d]{1,3}.[\d]{1,3}.[\d]{1,3}.[\d]{1,3})'
    pattern = re.compile(re_compile)
    result = pattern.findall(data)
    return result


if __name__ == '__main__':
    domain_list = [
        'github.com',
        'github.global.ssl.fastly.net',
        'github.community',
        'avatars.githubusercontent.com',
    ]
    image_list = [
        'avatars0.githubusercontent.com',
        'avatars1.githubusercontent.com',
        'avatars2.githubusercontent.com',
        'avatars3.githubusercontent.com',
        'avatars4.githubusercontent.com',
        'raw.githubusercontent.com',
        'cloud.githubusercontent.com',
        'camo.githubusercontent.com',
        'githubusercontent.com',
        'user-images.githubusercontent.com',
    ]
    url_ip_map = {}
    for url in domain_list:
        ips = get_IP_address_of_domain(url)
        if ips:
            url_ip_map[url] = ips[0]
            print(url + ': ' + ips[0])
    # 更新hosts列表
    hosts_path = '/etc/hosts'
    if os.name == 'nt':
        hosts_path = 'C:/Windows/System32/drivers/etc/hosts'
    result_hosts = []
    with open(hosts_path, mode='r') as f:
        lines = f.readlines()
        for i in range(len(lines)):
            line_list = re.split(r'[\s]{1,}', lines[i])
            if line_list[0].startswith('#') and line_list[1] in domain_list or line_list[1] in image_list:
                continue
            result_hosts.append(lines[i])
    for url, ip in url_ip_map.items():
        result_hosts.append(ip + '\t' + url + '\n')
    for image_url in image_list:
        result_hosts.append(url_ip_map['avatars.githubusercontent.com'] + '\t' + image_url + '\n')

    try:
        with open(hosts_path, 'w') as f:
            f.writelines(result_hosts)
    except PermissionError:
        raise PermissionError('更新失败，请使用管理员账户或使用sudo命令执行该程序')
    if os.name == 'nt':
        result = os.system('ipconfig /flushdns')
    elif sys.platform == 'darwin':
        result = os.system('sudo killall -HUP mDNSResponder')
    elif sys.platform == 'linux':
        result = os.system('sudo service restart')
    print('----------------------------------')
    if result == 0:
        print('更新 hosts 文件完成，刷新 DNS 缓存完成')
    else:
        print('更新 hosts 文件完成，需要刷新 DNS 缓存请参考下面命令')
        print('Windows 请执行命令: ipconfig /flushdns')
        print('Linux   请执行命令: sudo service nscd restart')
        print('               或: sudo service restart')
        print('               或: sudo systemctl restart network')
        print('               或: sudo /etc/init.d/networking restart')
        print('MacOS   请执行命令: sudo killall -HUP mDNSResponder')
        print('         Yosemite: sudo discoveryutil udnsflushcaches')
        print('     Snow Leopard: sudo dscacheutil -flushcache')
        print('Leopard and below: sudo lookupd -flushcache')
    print('----------------------------------')

# result = httpGetRequest('https://github.com.ipaddress.com/gist.github.com')
