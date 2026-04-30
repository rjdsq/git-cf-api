import os
import re

def merge_and_sort_files():
    # 1. 定义输入文件
    input_files = ['Cf.090227.xyz.txt', 'vps789.com.txt', 'cf-speed-dns.txt']
    merged_data = {}
    total_raw_count = 0

    # 2. 逐行读取，不做复杂的分割，只分地址和备注
    for file_name in input_files:
        if os.path.exists(file_name):
            with open(file_name, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    total_raw_count += 1
                    
                    # 只要有#，就拆分；没有#，整行都是地址
                    if '#' in line:
                        parts = line.split('#', 1)
                        addr = parts[0].strip()
                        remark = parts[1].strip()
                    else:
                        addr = line
                        remark = ""

                    if not addr:
                        continue

                    # 去重逻辑：同一个地址，把所有备注拼起来
                    if addr not in merged_data:
                        merged_data[addr] = []
                    
                    if remark and remark not in merged_data[addr]:
                        merged_data[addr].append(remark)

    # 3. 初始化 7 个优先级容器
    groups = {
        'domain_remark': [],    # 1. 域名有备注
        'telecom': [],          # 2. IP 电信
        'mobile': [],           # 3. IP 移动
        'unicom': [],           # 4. IP 联通
        'pure_ip_other': [],    # 5. IP 其他
        'pure_ip_none': [],     # 6. IP 无备注
        'domain_no_remark': []  # 7. 域名无备注
    }

    # 4. 严格归类
    for addr, remarks in merged_data.items():
        merged_remark = " | ".join(remarks)
        # 判断是否为纯 IP (IPv4)
        is_pure_ip = bool(re.match(r"^\d{1,3}(\.\d{1,3}){3}$", addr))

        if merged_remark:
            line_str = f"{addr}#{merged_remark}"
        else:
            line_str = addr

        if not is_pure_ip:
            # 域名类
            if merged_remark:
                groups['domain_remark'].append(line_str)
            else:
                groups['domain_no_remark'].append(line_str)
        else:
            # IP 类
            if not merged_remark:
                groups['pure_ip_none'].append(line_str)
            elif '电信' in merged_remark:
                groups['telecom'].append(line_str)
            elif '移动' in merged_remark:
                groups['mobile'].append(line_str)
            elif '联通' in merged_remark:
                groups['unicom'].append(line_str)
            else:
                groups['pure_ip_other'].append(line_str)

    # 5. 组内排序 (按整行长度)
    for key in groups:
        groups[key].sort(key=len)

    # 6. 组合最终结果
    final_output = []
    final_output.extend(groups['domain_remark'])
    final_output.extend(groups['telecom'])
    final_output.extend(groups['mobile'])
    final_output.extend(groups['unicom'])
    final_output.extend(groups['pure_ip_other'])
    final_output.extend(groups['pure_ip_none'])
    final_output.extend(groups['domain_no_remark'])

    final_count = len(final_output)
    duplicate_count = total_raw_count - final_count

    # 7. 打印详细对账日志
    overview = [
        "========== 采集汇总 ==========",
        f"初始总行数: {total_raw_count}",
        f"重复被过滤: {duplicate_count}",
        f"最终保留数: {final_count}",
        "---------- 分类详情 ----------",
        f"1. 域名+备注: {len(groups['domain_remark'])}",
        f"2. IP +电信: {len(groups['telecom'])}",
        f"3. IP +移动: {len(groups['mobile'])}",
        f"4. IP +联通: {len(groups['unicom'])}",
        f"5. IP +其他: {len(groups['pure_ip_other'])}",
        f"6. IP 无备注: {len(groups['pure_ip_none'])}",
        f"7. 域名无备注: {len(groups['domain_no_remark'])}",
        "=============================="
    ]

    for l in overview: print(l)

    # 8. 写文件
    with open('max.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(final_output) + '\n')

    with open('max.log', 'w', encoding='utf-8') as f:
        f.write('\n'.join(overview) + '\n')

if __name__ == '__main__':
    merge_and_sort_files()
