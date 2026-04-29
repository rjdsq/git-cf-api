import subprocess
import platform
import re

def ping_check(address):
    is_ipv6 = ":" in address and address.count(":") > 1
    
    if platform.system() != "Windows":
        cmd = ["ping", "-6" if is_ipv6 else "-4", "-c", "1", "-W", "2", address]
    else:
        cmd = ["ping", "-n", "1", "-w", "2000", address]
        
    try:
        result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return result.returncode == 0
    except:
        return False

def main():
    valid_lines = []
    
    try:
        with open("max.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        for line in lines:
            line = line.strip()
            if not line or "#" not in line:
                continue
            
            raw_part = line.split("#")[0].strip()
            host = raw_part
            if "]:" in host:
                host = host.split("]:")[0].replace("[", "")
            elif ":" in host and host.count(":") == 1:
                host = host.split(":")[0]
            
            if ping_check(host):
                valid_lines.append(line)

        with open("max.txt", "w", encoding="utf-8") as f:
            if valid_lines:
                f.write("\n".join(valid_lines) + "\n")

    except FileNotFoundError:
        pass

if __name__ == "__main__":
    main()
