import re
import requests
import os
import socket

API_LIST = [
    "https://bestcf.pages.dev/vps789/top20.txt",
    "https://bestcf.pages.dev/tiancheng/all.txt",
    "https://bestcf.pages.dev/vvhan/ipv4.txt",
    "https://bestcf.pages.dev/vvhan/ipv6.txt",
    "https://bestcf.pages.dev/xinyitang3/ipv4.txt",
    "https://bestcf.pages.dev/nirevil/ipv4.txt",
    "https://bestcf.pages.dev/mingyu/ipv4.txt",
    "https://bestcf.pages.dev/zhixuanwang/ipv4-onlyip.txt",
    "https://cf.090227.xyz/ip.164746.xyz",
    "https://cf.090227.xyz/CloudFlareYes",
    "https://cf.090227.xyz/cmcc?ips=8",
    "https://cf.090227.xyz/cu",
    "https://cf.090227.xyz/ct?ips=6"
]

DOMAIN_LIST = [
    "cf.tencentapp.cn",
    "cloudflare-dl.byoip.top",
    "cf.877774.xyz",
    "saas.sin.fan",
    "bestcf.030101.xyz"
]

IP_REG = re.compile(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|([0-9a-fA-F]{1,4}:){1,7}[0-9a-fA-F]{1,4})")

def fetch_content(url):
    try:
        headers = {"User-Agent":"Mozilla/5.0"}
        resp = requests.get(url,timeout=15,headers=headers)
        resp.raise_for_status()
        return resp.text
    except Exception:
        return ""

def parse_ip(line):
    match = IP_REG.search(line)
    if match:
        return match.group()
    return None

def resolve_domain(domain):
    res_list = []
    try:
        info = socket.getaddrinfo(domain, 443)
        for item in info:
            ip = item[4][0]
            res_list.append(f"{ip}:443#{domain}")
    except Exception:
        pass
    return res_list

def main():
    line_pool = []
    for url in API_LIST:
        text = fetch_content(url)
        lines = text.splitlines()
        for l in lines:
            s = l.strip()
            if s and parse_ip(s):
                line_pool.append(s)
    for d in DOMAIN_LIST:
        dom_lines = resolve_domain(d)
        line_pool.extend(dom_lines)
    unique_lines = list(set(line_pool))
    with open("max.txt","w",encoding="utf-8") as f:
        for row in unique_lines:
            f.write(row + "\n")

if __name__ == "__main__":
    main()
