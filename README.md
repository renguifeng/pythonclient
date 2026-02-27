# my_app - macOS 打包指南

## 快速开始

### 1. 推送代码到 GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin <your-repo-url>
git push -u origin main
```

### 2. 自动构建
推送后，GitHub Actions 会自动构建 macOS 可执行文件。

### 3. 下载可执行文件
1. 进入 GitHub 仓库页面
2. 点击 "Actions" 标签
3. 选择最新的工作流运行
4. 在 "Artifacts" 部分下载 `my_app-macos`

## 在 macOS 上运行

下载后，在终端执行：

```bash
# 解压下载的文件
unzip my_app-macos.zip

# 赋予执行权限
chmod +x my_app

# 移除苹果安全隔离（首次运行需要）
xattr -d com.apple.quarantine my_app

# 运行程序
./my_app
```

## 手动触发构建

在 GitHub 仓库页面：
1. 点击 "Actions"
2. 选择 "Build macOS Executable"
3. 点击 "Run workflow"

## 依赖管理

将你的 Python 依赖添加到 `requirements.txt` 文件中。
