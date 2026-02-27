#!/usr/bin/env python3
"""
Python 加密工具客户端示例

提供两种调用方式：
1. 类调用方式：通过 EncryptionClient 类进行 API 调用
2. 命令行方式：直接运行脚本进行加密操作

配置文件:
    默认配置文件路径: 与可执行文件同目录的 config.json
    可以通过 --config 指定自定义配置文件

    配置文件格式:
    {
        "base_url": "http://localhost:5050",
        "python_version": "3.11",
        "timeout": 300
    }

使用示例:
    # 初始化配置
    pyencrypt-client init

    # 命令行方式（使用配置文件中的默认值）
    pyencrypt-client encrypt-file --file my_project.zip
    pyencrypt-client encrypt-files --file main.py --file utils.py
    pyencrypt-client encrypt-text --name test.py --content "print('Hello')"

    # 类调用方式
    from client_example import EncryptionClient

    client = EncryptionClient(base_url="http://localhost:5000")
    result = client.encrypt_file("main.py", python_version="3.9")
"""
import argparse
import json
import os
import sys
from typing import Dict, List, Optional, Any
from pathlib import Path

try:
    import requests
except ImportError:
    print("错误: 需要安装 requests 库")
    print("请运行: pip install requests")
    sys.exit(1)


def get_default_config_path() -> Path:
    """获取默认配置文件路径（与可执行文件同目录）"""
    if getattr(sys, 'frozen', False):
        # 打包后，配置文件与可执行文件同目录
        exe_dir = Path(sys.executable).parent
    else:
        # 开发模式，配置文件在当前脚本目录
        exe_dir = Path(__file__).parent
    return exe_dir / "config.json"


# 默认配置文件路径
DEFAULT_CONFIG_FILE = get_default_config_path()


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    加载配置文件

    参数:
        config_path: 配置文件路径，如果为 None 则使用默认路径

    返回:
        配置字典
    """
    if config_path:
        config_file = Path(config_path)
    else:
        config_file = DEFAULT_CONFIG_FILE

    default_config = {
        "base_url": "http://localhost:5000",
        "python_version": None,
        "timeout": 300
    }

    if not config_file.exists():
        return default_config

    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
            # 合并默认配置
            for key in default_config:
                if key not in config:
                    config[key] = default_config[key]
            return config
    except Exception as e:
        print(f"警告: 读取配置文件失败 ({e})，使用默认配置")
        return default_config


def save_config(config: Dict[str, Any], config_path: Optional[str] = None) -> bool:
    """
    保存配置文件

    参数:
        config: 配置字典
        config_path: 配置文件路径，如果为 None 则使用默认路径

    返回:
        是否保存成功
    """
    if config_path:
        config_file = Path(config_path)
    else:
        config_file = DEFAULT_CONFIG_FILE

    try:
        config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"错误: 保存配置文件失败 ({e})")
        return False


def show_config(config_path: Optional[str] = None):
    """显示当前配置"""
    config = load_config(config_path)
    config_file = config_path or str(DEFAULT_CONFIG_FILE)

    print(f"配置文件: {config_file}")
    print("-" * 40)
    print(f"  base_url:       {config.get('base_url', '未设置')}")
    print(f"  python_version: {config.get('python_version') or '未设置'}")
    print(f"  timeout:        {config.get('timeout', 300)} 秒")


def init_config(config_path: Optional[str] = None):
    """初始化配置文件（交互式）"""
    config_file = config_path or str(DEFAULT_CONFIG_FILE)

    print(f"初始化配置文件: {config_file}")
    print("-" * 40)

    # 加载现有配置
    config = load_config(config_path)

    # 交互式输入
    base_url = input(f"服务地址 [{config.get('base_url', 'http://localhost:5000')}]: ").strip()
    if base_url:
        config['base_url'] = base_url

    python_version = input(f"默认 Python 版本 [{config.get('python_version') or '不指定'}]: ").strip()
    if python_version:
        config['python_version'] = python_version
    elif python_version == '' and 'python_version' in config:
        # 如果输入为空，保持不设置
        pass

    timeout = input(f"超时时间/秒 [{config.get('timeout', 300)}]: ").strip()
    if timeout:
        try:
            config['timeout'] = int(timeout)
        except ValueError:
            print("超时时间必须是数字，保持原值")

    if save_config(config, config_path):
        print(f"\n✅ 配置已保存到: {config_file}")
        show_config(config_path)
    else:
        print("\n❌ 配置保存失败")


def cmd_init(args):
    """处理 init 命令"""
    init_config(getattr(args, 'config', None))
    return 0


class EncryptionClient:
    """Python 加密工具 API 客户端"""

    def __init__(self, base_url: str = "http://localhost:5000", timeout: int = 300):
        """
        初始化客户端

        参数:
            base_url: 服务地址，默认为 http://localhost:5000
            timeout: 请求超时时间（秒），默认 300 秒（5分钟，因为编译可能需要较长时间）
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout

    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        发送 HTTP 请求

        参数:
            method: HTTP 方法
            endpoint: API 端点
            **kwargs: 传递给 requests 的其他参数

        返回:
            响应 JSON 数据

        异常:
            requests.exceptions.RequestException: 请求失败
        """
        url = f"{self.base_url}{endpoint}"
        kwargs.setdefault('timeout', self.timeout)

        response = requests.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json()

    def _download(self, endpoint: str, output_path: str) -> str:
        """
        下载文件

        参数:
            endpoint: API 端点
            output_path: 输出文件路径

        返回:
            保存的文件路径
        """
        url = f"{self.base_url}{endpoint}"
        response = requests.get(url, timeout=self.timeout, stream=True)
        response.raise_for_status()

        # 确保输出目录存在
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        return output_path

    def get_python_versions(self) -> Dict[str, Any]:
        """
        获取可用的 Python 版本列表

        返回:
            包含版本列表和默认版本的字典
            {
                "versions": [
                    {"version": "3.9", "full_version": "Python 3.9.18", "path": "/usr/bin/python3.9"}
                ],
                "default_version": {"version": "3.9", "full_version": "Python 3.9.18", "path": "/usr/bin/python3"}
            }
        """
        return self._request('GET', '/api/python-versions')

    def health_check(self) -> Dict[str, Any]:
        """
        健康检查

        返回:
            {"status": "ok"}
        """
        return self._request('GET', '/health')

    def encrypt_file(self, file_path: str, python_version: Optional[str] = None) -> Dict[str, Any]:
        """
        上传单个文件（ZIP 或 Python 文件）进行加密

        参数:
            file_path: 文件路径
            python_version: Python 版本（可选）

        返回:
            加密结果
            {
                "success": true,
                "message": "处理完成",
                "output_file": "encrypted_xxx.zip",
                "download_url": "/download/encrypted_xxx.zip",
                "readme_file": "encrypted_xxx_README.txt",
                "stats": {"total_files": 1, "compiled_files": 1, "failed_count": 0},
                "failed_files": []
            }
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")

        filename = os.path.basename(file_path)
        is_zip = filename.lower().endswith('.zip')

        with open(file_path, 'rb') as f:
            if is_zip:
                files = {'file': (filename, f)}
            else:
                files = {'files': (filename, f)}

            data = {}
            if python_version:
                data['python_version'] = python_version

            response = requests.post(
                f"{self.base_url}/api/encrypt-file",
                files=files,
                data=data,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()

    def encrypt_files(self, file_paths: List[str], python_version: Optional[str] = None) -> Dict[str, Any]:
        """
        上传多个 Python 文件进行加密

        参数:
            file_paths: 文件路径列表
            python_version: Python 版本（可选）

        返回:
            加密结果
        """
        # 检查文件是否存在
        for path in file_paths:
            if not os.path.exists(path):
                raise FileNotFoundError(f"文件不存在: {path}")

        # 准备多文件上传
        files = [('files', (os.path.basename(path), open(path, 'rb'))) for path in file_paths]
        data = {}

        if python_version:
            data['python_version'] = python_version

        try:
            response = requests.post(
                f"{self.base_url}/api/encrypt-file",
                files=files,
                data=data,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        finally:
            # 关闭所有打开的文件
            for _, (_, f) in files:
                f.close()

    def encrypt_code(self, files: List[Dict[str, str]], python_version: Optional[str] = None) -> Dict[str, Any]:
        """
        直接加密代码文本

        参数:
            files: 文件列表，每个元素包含 filename 和 content
                [
                    {"filename": "main.py", "content": "print('Hello')"},
                    {"filename": "utils.py", "content": "def add(a, b): return a + b"}
                ]
            python_version: Python 版本（可选）

        返回:
            加密结果
        """
        payload = {'files': files}
        if python_version:
            payload['python_version'] = python_version

        return self._request(
            'POST',
            '/api/encrypt',
            json=payload,
            headers={'Content-Type': 'application/json'}
        )

    def download_result(self, filename: str, output_dir: str = ".") -> str:
        """
        下载加密结果文件

        参数:
            filename: 输出文件名
            output_dir: 输出目录

        返回:
            保存的文件路径
        """
        output_path = os.path.join(output_dir, filename)
        return self._download(f'/download/{filename}', output_path)

    def get_readme(self, filename: str) -> str:
        """
        获取 README 内容

        参数:
            filename: README 文件名

        返回:
            README 内容
        """
        result = self._request('GET', f'/readme/{filename}')
        return result.get('content', '')

    def list_outputs(self) -> List[Dict[str, Any]]:
        """
        列出所有可下载的输出文件

        返回:
            文件列表
            [
                {"name": "encrypted_xxx.zip", "size": 1024, "mtime": 1704067200.0, "mtime_iso": "2024-01-01T12:00:00"}
            ]
        """
        result = self._request('GET', '/outputs')
        return result.get('files', [])

    def delete_output(self, filename: str) -> bool:
        """
        删除输出文件

        参数:
            filename: 文件名

        返回:
            是否成功
        """
        result = self._request('DELETE', f'/outputs/{filename}')
        return result.get('success', False)


def cmd_encrypt_file(args):
    """处理 encrypt-file 命令"""
    client = EncryptionClient(base_url=args.base_url, timeout=args.timeout)

    print(f"正在上传文件: {args.file}")
    if args.python_version:
        print(f"使用 Python 版本: {args.python_version}")

    try:
        result = client.encrypt_file(args.file, args.python_version)

        if result.get('success'):
            stats = result.get('stats', {})
            failed_files = result.get('failed_files', [])

            if failed_files:
                print(f"\n⚠️ {result.get('message')}")
                print(f"输出文件: {result.get('output_file')}")
                print(f"\n编译失败的文件:")
                for f in failed_files:
                    print(f"  - {f.get('filename')}: {f.get('error')}")
            else:
                print(f"\n✅ {result.get('message')}")
                print(f"输出文件: {result.get('output_file')}")

            print(f"下载链接: {args.base_url}{result.get('download_url')}")

            if args.output:
                output_path = client.download_result(result['output_file'], args.output)
                print(f"已下载到: {output_path}")

            if failed_files:
                return 1
        else:
            print(f"\n❌ 加密失败: {result.get('error')}")
            return 1
    except Exception as e:
        print(f"\n❌ 请求失败: {e}")
        return 1

    return 0


def cmd_encrypt_files(args):
    """处理 encrypt-files 命令（多文件）"""
    client = EncryptionClient(base_url=args.base_url, timeout=args.timeout)

    print(f"正在上传 {len(args.files)} 个文件...")
    if args.python_version:
        print(f"使用 Python 版本: {args.python_version}")

    try:
        result = client.encrypt_files(args.files, args.python_version)

        if result.get('success'):
            failed_files = result.get('failed_files', [])

            if failed_files:
                print(f"\n⚠️ {result.get('message')}")
                print(f"输出文件: {result.get('output_file')}")
                print(f"\n编译失败的文件:")
                for f in failed_files:
                    print(f"  - {f.get('filename')}: {f.get('error')}")
            else:
                print(f"\n✅ {result.get('message')}")
                print(f"输出文件: {result.get('output_file')}")

            print(f"下载链接: {args.base_url}{result.get('download_url')}")

            if args.output:
                output_path = client.download_result(result['output_file'], args.output)
                print(f"已下载到: {output_path}")

            if failed_files:
                return 1
        else:
            print(f"\n❌ 加密失败: {result.get('error')}")
            return 1
    except Exception as e:
        print(f"\n❌ 请求失败: {e}")
        return 1

    return 0


def cmd_encrypt_code(args):
    """处理 encrypt-code 命令（读取本地文件并通过代码文本 API 加密）"""
    client = EncryptionClient(base_url=args.base_url, timeout=args.timeout)

    # 读取文件内容
    files = []
    for file_path in args.files:
        if not os.path.exists(file_path):
            print(f"❌ 文件不存在: {file_path}")
            return 1
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        files.append({
            'filename': os.path.basename(file_path),
            'content': content
        })

    print(f"正在加密 {len(files)} 个文件（通过代码文本 API）...")
    if args.python_version:
        print(f"使用 Python 版本: {args.python_version}")

    try:
        result = client.encrypt_code(files, args.python_version)

        if result.get('success'):
            failed_files = result.get('failed_files', [])

            if failed_files:
                print(f"\n⚠️ {result.get('message')}")
                print(f"输出文件: {result.get('output_file')}")
                print(f"\n编译失败的文件:")
                for f in failed_files:
                    print(f"  - {f.get('filename')}: {f.get('error')}")
            else:
                print(f"\n✅ {result.get('message')}")
                print(f"输出文件: {result.get('output_file')}")

            print(f"下载链接: {args.base_url}{result.get('download_url')}")

            if args.output:
                output_path = client.download_result(result['output_file'], args.output)
                print(f"已下载到: {output_path}")

            if failed_files:
                return 1
        else:
            print(f"\n❌ 加密失败: {result.get('error')}")
            return 1
    except Exception as e:
        print(f"\n❌ 请求失败: {e}")
        return 1

    return 0


def cmd_encrypt_text(args):
    """处理 encrypt-text 命令（直接传递代码文本）"""
    client = EncryptionClient(base_url=args.base_url, timeout=args.timeout)

    files = [{'filename': args.name, 'content': args.content}]

    print(f"正在加密代码文本: {args.name}")
    if args.python_version:
        print(f"使用 Python 版本: {args.python_version}")

    try:
        result = client.encrypt_code(files, args.python_version)

        if result.get('success'):
            failed_files = result.get('failed_files', [])

            if failed_files:
                print(f"\n⚠️ {result.get('message')}")
                print(f"输出文件: {result.get('output_file')}")
                print(f"\n编译失败的文件:")
                for f in failed_files:
                    print(f"  - {f.get('filename')}: {f.get('error')}")
            else:
                print(f"\n✅ {result.get('message')}")
                print(f"输出文件: {result.get('output_file')}")

            print(f"下载链接: {args.base_url}{result.get('download_url')}")

            if args.output:
                output_path = client.download_result(result['output_file'], args.output)
                print(f"已下载到: {output_path}")

            if failed_files:
                return 1
        else:
            print(f"\n❌ 加密失败: {result.get('error')}")
            return 1
    except Exception as e:
        print(f"\n❌ 请求失败: {e}")
        return 1

    return 0


def cmd_list(args):
    """处理 list 命令"""
    client = EncryptionClient(base_url=args.base_url, timeout=args.timeout)

    try:
        files = client.list_outputs()

        if not files:
            print("没有可下载的文件")
            return 0

        print(f"共 {len(files)} 个文件:")
        print("-" * 80)
        print(f"{'文件名':<50} {'大小':>15} {'修改时间':>20}")
        print("-" * 80)

        for f in files:
            size = f.get('size', 0)
            size_str = f"{size / 1024:.1f} KB" if size > 1024 else f"{size} B"
            mtime = f.get('mtime_iso', 'N/A')
            print(f"{f['name']:<50} {size_str:>15} {mtime:>20}")

    except Exception as e:
        print(f"❌ 获取文件列表失败: {e}")
        return 1

    return 0


def cmd_download(args):
    """处理 download 命令"""
    client = EncryptionClient(base_url=args.base_url, timeout=args.timeout)

    try:
        output_path = client.download_result(args.filename, args.output)
        print(f"✅ 已下载到: {output_path}")
    except Exception as e:
        print(f"❌ 下载失败: {e}")
        return 1

    return 0


def cmd_delete(args):
    """处理 delete 命令"""
    client = EncryptionClient(base_url=args.base_url, timeout=args.timeout)

    try:
        if client.delete_output(args.filename):
            print(f"✅ 已删除: {args.filename}")
        else:
            print(f"❌ 删除失败")
            return 1
    except Exception as e:
        print(f"❌ 删除失败: {e}")
        return 1

    return 0


def cmd_versions(args):
    """处理 versions 命令"""
    client = EncryptionClient(base_url=args.base_url, timeout=args.timeout)

    try:
        result = client.get_python_versions()
        versions = result.get('versions', [])
        default = result.get('default_version', {})

        print("可用的 Python 版本:")
        print("-" * 60)

        for v in versions:
            marker = " (默认)" if v.get('version') == default.get('version') else ""
            print(f"  Python {v.get('version')}: {v.get('full_version')}{marker}")
            print(f"    路径: {v.get('path')}")

        if not versions:
            print("  没有找到可用的 Python 版本")

    except Exception as e:
        print(f"❌ 获取版本列表失败: {e}")
        return 1

    return 0


def cmd_status(args):
    """处理 status 命令"""
    client = EncryptionClient(base_url=args.base_url, timeout=args.timeout)

    try:
        result = client.health_check()
        if result.get('status') == 'ok':
            print(f"✅ 服务正常: {args.base_url}")
        else:
            print(f"⚠️ 服务状态异常: {result}")
            return 1
    except Exception as e:
        print(f"❌ 服务不可用: {e}")
        return 1

    return 0


def print_full_usage():
    """打印完整的使用说明"""
    print("""
╔═══════════════════════════════════════════════════════════════════════════╗
║                    Python 加密工具客户端 v1.0                               ║
╚═══════════════════════════════════════════════════════════════════════════╝

【用法】  pyencrypt-client [选项] <命令> [参数]

【选项】  --config <文件>    指定配置文件 (默认: 同目录 config.json)
         --base-url <URL>   服务地址
         --timeout <秒>     超时时间 (默认: 300)

【命令】  init          初始化配置文件
         config        查看当前配置
         status        检查服务状态
         versions      查看可用 Python 版本
         encrypt-file  上传单个文件加密 (ZIP/.py)
         encrypt-files 上传多个文件加密
         encrypt-code  通过 API 加密代码
         encrypt-text  直接加密代码文本
         list          列出输出文件
         download      下载加密结果
         delete        删除输出文件

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【示例】

  # 初始化配置（首次使用）
  pyencrypt-client init

  # 加密单个文件
  pyencrypt-client encrypt-file --file main.py --output ./dist/

  # 加密 ZIP 项目
  pyencrypt-client encrypt-file --file project.zip --output ./dist/

  # 加密多个文件
  pyencrypt-client encrypt-files --files main.py --files utils.py --files config.py --output ./dist/

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")


def cmd_init(args):
    """处理 init 命令"""
    init_config(getattr(args, 'config', None))
    return 0


def cmd_config(args):
    """处理 config 命令"""
    show_config(getattr(args, 'config', None))
    return 0


def main():
    # 如果不带任何参数，显示完整用法
    if len(sys.argv) == 1:
        print_full_usage()
        return 0

    # 处理 -h 或 --help
    if '-h' in sys.argv or '--help' in sys.argv:
        print_full_usage()
        return 0

    # 首先解析 --config 参数（如果有的话）
    config_path = None
    for i, arg in enumerate(sys.argv):
        if arg == '--config' and i + 1 < len(sys.argv):
            config_path = sys.argv[i + 1]
            break

    # 加载配置文件
    config = load_config(config_path)

    parser = argparse.ArgumentParser(
        description='Python 加密工具客户端',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=False
    )

    # 全局参数（配置文件值作为默认值）
    parser.add_argument('--config', help='配置文件路径')
    parser.add_argument('--base-url', default=config.get('base_url', 'http://localhost:5000'),
                        help=f"服务地址 (默认: {config.get('base_url', 'http://localhost:5000')})")
    parser.add_argument('--timeout', type=int, default=config.get('timeout', 300),
                        help=f"请求超时时间/秒 (默认: {config.get('timeout', 300)})")

    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # init 命令
    subparsers.add_parser('init', help='初始化配置文件')

    # config 命令
    subparsers.add_parser('config', help='查看当前配置')

    # status 命令
    subparsers.add_parser('status', help='检查服务状态')

    # versions 命令
    subparsers.add_parser('versions', help='查看可用的 Python 版本')

    # encrypt-file 命令
    p_encrypt_file = subparsers.add_parser('encrypt-file', help='上传文件进行加密')
    p_encrypt_file.add_argument('--file', required=True, help='要加密的文件路径 (ZIP 或 .py)')
    p_encrypt_file.add_argument('--python-version', default=config.get('python_version'),
                                 help=f"Python 版本 (默认: {config.get('python_version') or '不指定'})")
    p_encrypt_file.add_argument('--output', '-o', help='下载结果到指定目录')

    # encrypt-files 命令
    p_encrypt_files = subparsers.add_parser('encrypt-files', help='上传多个 Python 文件进行加密')
    p_encrypt_files.add_argument('--files', '-f', required=True, action='append', help='要加密的文件路径')
    p_encrypt_files.add_argument('--python-version', default=config.get('python_version'),
                                  help=f"Python 版本 (默认: {config.get('python_version') or '不指定'})")
    p_encrypt_files.add_argument('--output', '-o', help='下载结果到指定目录')

    # encrypt-code 命令
    p_encrypt_code = subparsers.add_parser('encrypt-code', help='通过代码文本 API 加密文件')
    p_encrypt_code.add_argument('--files', '-f', required=True, action='append', help='要加密的文件路径')
    p_encrypt_code.add_argument('--python-version', default=config.get('python_version'),
                                 help=f"Python 版本 (默认: {config.get('python_version') or '不指定'})")
    p_encrypt_code.add_argument('--output', '-o', help='下载结果到指定目录')

    # encrypt-text 命令
    p_encrypt_text = subparsers.add_parser('encrypt-text', help='直接加密代码文本')
    p_encrypt_text.add_argument('--name', required=True, help='文件名 (如 test.py)')
    p_encrypt_text.add_argument('--content', required=True, help='代码内容')
    p_encrypt_text.add_argument('--python-version', default=config.get('python_version'),
                                 help=f"Python 版本 (默认: {config.get('python_version') or '不指定'})")
    p_encrypt_text.add_argument('--output', '-o', help='下载结果到指定目录')

    # list 命令
    subparsers.add_parser('list', help='列出所有可下载的输出文件')

    # download 命令
    p_download = subparsers.add_parser('download', help='下载加密结果')
    p_download.add_argument('filename', help='要下载的文件名')
    p_download.add_argument('--output', '-o', default='.', help='输出目录 (默认: 当前目录)')

    # delete 命令
    p_delete = subparsers.add_parser('delete', help='删除输出文件')
    p_delete.add_argument('filename', help='要删除的文件名')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    # 分发命令
    commands = {
        'init': cmd_init,
        'config': cmd_config,
        'status': cmd_status,
        'versions': cmd_versions,
        'encrypt-file': cmd_encrypt_file,
        'encrypt-files': cmd_encrypt_files,
        'encrypt-code': cmd_encrypt_code,
        'encrypt-text': cmd_encrypt_text,
        'list': cmd_list,
        'download': cmd_download,
        'delete': cmd_delete,
    }

    handler = commands.get(args.command)
    if handler:
        return handler(args)
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())
