import socket
import concurrent.futures
import sys

def check_tcp_ping(line):
    line = line.strip()
    if not line:
        return None
    try:
        left_part = line.split('#')[0].strip()
        
        if left_part.startswith('['):
            host = left_part.split(']')[0][1:]
            port_str = left_part.split(']')[-1]
            if port_str.startswith(':'):
                port = int(port_str[1:])
            else:
                port = 443
        else:
            if ':' in left_part:
                host, port_str = left_part.split(':', 1)
                port = int(port_str)
            else:
                host = left_part
                port = 443
                
        with socket.create_connection((host, port), timeout=2):
            pass
            
        print(f"[保留] 端口开放: {host}:{port}")
        return line
        
    except (socket.timeout, ConnectionRefusedError, OSError):
        print(f"[丢弃] 无法连通: {host}:{port}")
        return None
    except Exception:
        print(f"[错误] 解析或测试异常: {line}")
        return None

if __name__ == '__main__':
    print("=== 开始执行 TCP 端口清洗任务 ===")
    
    try:
        with open('max.txt', 'r', encoding='utf-8') as f:
            lines = [line for line in f.readlines() if line.strip()]
    except FileNotFoundError:
        print("错误: 找不到 max.txt 文件！")
        sys.exit(1)
        
    total_count = len(lines)
    print(f"-> 成功读取 max.txt，共发现 {total_count} 个待测目标。")
    print("-> 正在启动 50 线程并发 TCP 检测...\n")
    
    valid_lines = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        for res in executor.map(check_tcp_ping, lines):
            if res:
                valid_lines.append(res)
                
    kept_count = len(valid_lines)
    discarded_count = total_count - kept_count
    
    print("\n=== 检测过程结束 ===")
    print(f"统计信息:")
    print(f"  - 初始目标总数: {total_count}")
    print(f"  - 成功保留数量: {kept_count}")
    print(f"  - 超时丢弃数量: {discarded_count}")
    
    with open('max.txt', 'w', encoding='utf-8') as f:
        for line in valid_lines:
            f.write(line + '\n')
            
    print("-> 存活的节点已重新写入 max.txt。")
