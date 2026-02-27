# pyencrypt-client

Python 加密工具客户端 - macOS 版本

## 在 macOS 上运行

下载后，在终端执行：

```bash
# 解压下载的文件
unzip pyencrypt-client-macos.zip

# 赋予执行权限
chmod +x pyencrypt-client

# 移除苹果安全隔离（首次运行需要）
xattr -d com.apple.quarantine pyencrypt-client

# 运行程序
./pyencrypt-client
```

## 使用方法

```bash
# 查看帮助
./pyencrypt-client

# 初始化配置
./pyencrypt-client init

# 检查服务状态
./pyencrypt-client status --base-url http://your-server:5000

# 加密文件
./pyencrypt-client encrypt-file --file main.py --output ./dist/
```
