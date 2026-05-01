import os
import datetime

def merge_and_sort_files():
    input_files = ['cf.090227.xyz.txt', 'vps789.com.txt', 'cf-speed-dns.txt']
    merged_data = {}
    duplicate_details = []
    total_raw_count = 0

    # 修正时区（北京时间）
    bj_time = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
    
    # 构建自定义格式：月/日/时:分 (去除前导零，全部用 / 分隔)
    # 示例结果：8/5/18:6
    month = bj_time.month
    day = bj_time.day
    hour = bj_time.hour
    minute = bj_time.minute
    time_str = f"{month}/{day}/{hour}:{minute}"

    for file_name in input_files:
        if os.path.exists(file_name):
            with open(file_name, 'r', encoding='utf-8') as f:
                for line in f:
                    # 保留原始行内容（含空格），仅去换行符
                    raw_line = line.replace('\n', '').replace('\r', '')
                    if not raw_line.strip():
                        continue
                    
                    total_raw_count += 1
                    
                    if '#' in raw_line:
                        parts = raw_line.split('#', 1)
                        addr = parts[0] # 完全保留原始格式（包括空格）
                        remark = parts[1].strip()
                    else:
                        addr = raw_line
                        remark = ""

                    if addr not in merged_data:
                        merged_data[addr] = []
                    else:
                        # 记录详细过滤清单：保留原始格式的地址和来源文件名
                        duplicate_details.append(f"重复详情: 地址 [{addr}] 在文件 [{file_name}] 中重复出现")
                    
                    if remark and remark not in merged_data[addr]:
                        merged_data[addr].append(remark)

    groups = {
        'domain_remark': [], 'telecom': [], 'mobile': [], 
        'unicom': [], 'ip_other': [], 'ip_none': [], 'domain_none': []
    }

    for addr, remarks in merged_data.items():
        # 备注逻辑：addr#原备注 | 8/5/18:6
        if remarks:
            merged_remark = " | ".join(remarks) + f" | {time_str}"
        else:
            merged_remark = time_str

        is_domain = any(c.isalpha() for c in addr)
        line_str = f"{addr}#{merged_remark}"

        if is_domain:
            if remarks: groups['domain_remark'].append(line_str)
            else: groups['domain_none'].append(line_str)
        else:
            raw_remarks_str = " ".join(remarks)
            if not remarks: groups['ip_none'].append(line_str)
            elif '电信' in raw_remarks_str: groups['telecom'].append(line_str)
            elif '移动' in raw_remarks_str: groups['mobile'].append(line_str)
            elif '联通' in raw_remarks_str: groups['unicom'].append(line_str)
            else: groups['ip_other'].append(line_str)

    # 汇总输出 (一行一个，无空行)
    final_output = []
    order = ['domain_remark', 'telecom', 'mobile', 'unicom', 'ip_other', 'ip_none', 'domain_none']
    for key in order:
        groups[key].sort(key=len)
        final_output.extend(groups[key])

    final_count = len(merged_data)
    
    # 构造日志内容
    log_content = [
        "========== 采集汇总 ==========",
        f"北京时间: {time_str}",
        f"总读取行数: {total_raw_count}",
        f"去重后总数: {final_count}",
        f"累计过滤重复次数: {len(duplicate_details)}",
        "---------- 详细过滤清单 ----------"
    ]
    if duplicate_details:
        log_content.extend(duplicate_details)
    else:
        log_content.append("此轮采集未发现重复项")
    log_content.append("----------------------------------")

    # 控制台打印
    for l in log_content: print(l)

    # 写入 max.txt
    with open('max.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(final_output) + '\n')

    # 写入 max.log
    with open('max.log', 'w', encoding='utf-8') as f:
        f.write('\n'.join(log_content) + '\n')

if __name__ == '__main__':
    merge_and_sort_files()
