#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <sys/socket.h>
#include <sys/un.h>

/**
 * 1. NVRAM 相关劫持
 */

char *nvram_get(const char *key) {
    // 增加一个调试打印，这样你能在屏幕上看到程序到底查了哪些键
    // printf("[nvram_get] query: %s\n", key);

    if (strcmp(key, "lan_ipaddr") == 0) {
        return "127.0.0.1";
    }
    if (strcmp(key, "lan_port") == 0) {
        return "80";
    }
    if (strcmp(key, "eth_port_map") == 0) {
        return "1";
    }
    if (strcmp(key, "wan_ifname") == 0) {
        return "br0";
    }
    
    return "0";
}

int nvram_set(const char *key, const char *value) {
    return 0;
}

int nvram_commit() {
    return 0;
}

/**
 * 2. IPC 通信劫持 (解决 connect cfm failed)
 */

// 劫持连接函数
int connect(int sockfd, const struct sockaddr *addr, socklen_t addrlen) {
    // 如果程序尝试连接 Unix Domain Socket (本地套接字文件)
    if (addr->sa_family == AF_UNIX) {
        // struct sockaddr_un *u_addr = (struct sockaddr_un *)addr;
        // printf("[connect] Hijacked Unix Socket connection to: %s\n", u_addr->sun_path);
        return 0; // 强行返回成功
    }
    return 0; 
}

// 劫持发送函数，假装数据发出了
ssize_t send(int sockfd, const void *buf, size_t len, int flags) {
    return len;
}

// 劫持接收函数，假装收到了成功回执（通常返回 1 即可骗过大多数检查）
ssize_t recv(int sockfd, void *buf, size_t len, int flags) {
    return len;
}

// 部分 Tenda 固件还会用这组函数
ssize_t sendto(int sockfd, const void *buf, size_t len, int flags,
               const struct sockaddr *dest_addr, socklen_t addrlen) {
    return len;
}

ssize_t recvfrom(int sockfd, void *buf, size_t len, int flags,
                 struct sockaddr *src_addr, socklen_t *addrlen) {
    return len;
}