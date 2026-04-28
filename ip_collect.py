import re
import requests
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

IPV4_REG = re.compile(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")
IPV6_REG = re.compile(r"([0-9a-fA-F]{1,4}:){2,}[0-9a-fA-F]{0,4}")
AREA_REG = re.compile(r"([A-Z]{2})\s*\|\s*")

def get(url):
    try:
        hd = {"User-Agent":"Mozilla/5.0"}
        return requests.get(url,timeout=12,headers=hd).text
    except:
        return ""

def get_area(text):
    m = AREA_REG.search(text)
    if m:
        return m.group(1)
    return ""

def get_only_ip(raw):
    ip4 = IPV4_REG.search(raw)
    ip6 = IPV6_REG.search(raw)
    if ip4:
        return ip4.group()
    if ip6:
        return ip6.group()
    return None

def rebuild_line(raw):
    ip = get_only_ip(raw)
    area = get_area(raw)
    base = raw.split("#")[0]
    if area:
        new_suffix = f"{area} | {ip}"
    else:
        new_suffix = ip
    return f"{base}#{new_suffix}"

def domain_to_lines(domain):
    out = []
    try:
        addr = socket.getaddrinfo(domain,443)
        for item in addr:
            ip = item[4][0]
            out.append([ip, f"{ip}:443#{domain}"])
    except:
        pass
    return out

def main():
    ip_seen = set()
    final_lines = []
    for api in API_LIST:
        txt = get(api)
        lines = txt.splitlines()
        for line in lines:
            s = line.strip()
            if not s:
                continue
            ip = get_only_ip(s)
            if not ip or ip in ip_seen:
                continue
            ip_seen.add(ip)
            new_line = rebuild_line(s)
            final_lines.append(new_line)
    for d in DOMAIN_LIST:
        d_list = domain_to_lines(d)
        for real_ip,line in d_list:
            if real_ip not in ip_seen:
                ip_seen.add(real_ip)
                final_lines.append(line)
    with open("max.txt","w",encoding="utf-8") as f:
        for item in final_lines:
            f.write(item + "\n")

if __name__ == "__main__":
    main()
