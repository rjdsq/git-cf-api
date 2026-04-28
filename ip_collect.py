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
# 匹配: 两个大写字母 + 任意空白符 + | + 任意空白符
AREA_REG = re.compile(r"([A-Z]{2})(\s*\|\s*)")

# 常用国家代码字典 (国旗 + 中文名称)
COUNTRY_MAP = {
    "US": "🇺🇸 美国", "HK": "🇭🇰 香港", "SG": "🇸🇬 新加坡", "JP": "🇯🇵 日本",
    "KR": "🇰🇷 韩国", "TW": "🇹🇼 台湾", "GB": "🇬🇧 英国", "UK": "🇬🇧 英国",
    "DE": "🇩🇪 德国", "NL": "🇳🇱 荷兰", "FR": "🇫🇷 法国", "AU": "🇦🇺 澳大利亚",
    "CA": "🇨🇦 加拿大", "IN": "🇮🇳 印度", "BR": "🇧🇷 巴西", "ZA": "🇿🇦 南非",
    "RU": "🇷🇺 俄罗斯", "MY": "🇲🇾 马来西亚", "ID": "🇮🇩 印尼", "TH": "🇹🇭 泰国",
    "VN": "🇻🇳 越南", "PH": "🇵🇭 菲律宾", "AE": "🇦🇪 阿联酋", "MO": "🇲🇴 澳门",
    "CN": "🇨🇳 中国", "IT": "🇮🇹 意大利", "ES": "🇪🇸 西班牙", "CH": "🇨🇭 瑞士",
    "SE": "🇸🇪 瑞典", "NO": "🇳🇴 挪威", "DK": "🇩🇰 丹麦", "FI": "🇫🇮 芬兰",
    "PL": "🇵🇱 波兰", "TR": "🇹🇷 土耳其", "AR": "🇦🇷 阿根廷", "MX": "🇲🇽 墨西哥"
}

def get(url):
    try:
        hd = {"User-Agent": "Mozilla/5.0"}
        return requests.get(url, timeout=12, headers=hd).text
    except:
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
    if not ip:
        return raw

    # 通过是否含有冒号来判断是否为 IPv6
    is_ipv6 = ":" in ip

    # 拆分 base 和 remark，最多只拆分一次
    parts = raw.split("#", 1)
    base = parts[0]
    remark = parts[1] if len(parts) > 1 else ""

    if is_ipv6:
        # IPv6的备注全部统一为：优选IPV6
        return f"{base}#优选IPV6"

    if remark:
        # 替换匹配到的国家代码，并保留 | 符号及其周围的空格
        def replacer(match):
            code = match.group(1)
            separator = match.group(2)
            if code in COUNTRY_MAP:
                return f"{COUNTRY_MAP[code]}{separator}"
            return match.group(0)

        # 仅在备注部分进行替换，不丢失后面的原始内容
        new_remark = AREA_REG.sub(replacer, remark)
        return f"{base}#{new_remark}"
    else:
        # 如果获取到的节点没有备注，则退化使用 IP 作为它的备注
        return f"{base}#{ip}"

def domain_to_lines(domain):
    out = []
    try:
        addr = socket.getaddrinfo(domain, 443)
        for item in addr:
            ip = item[4][0]
            is_ipv6 = ":" in ip

            if is_ipv6:
                # 修复IPv6容易被识别成域名的错误，并规范化 IPv6 + 端口 的格式
                base = f"[{ip}]:443" if not ip.startswith("[") else f"{ip}:443"
                remark = "优选IPV6"
            else:
                base = f"{ip}:443"
                remark = domain

            out.append([ip, f"{base}#{remark}"])
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
        for real_ip, line in d_list:
            if real_ip not in ip_seen:
                ip_seen.add(real_ip)
                final_lines.append(line)
                
    with open("max.txt", "w", encoding="utf-8") as f:
        for item in final_lines:
            f.write(item + "\n")

if __name__ == "__main__":
    main()
