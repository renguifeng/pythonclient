#!/usr/bin/env python3
"""示例 CLI 应用"""

import argparse


def main():
    parser = argparse.ArgumentParser(description='一个简单的示例程序')
    parser.add_argument('-n', '--name', default='World', help='要问候的名字')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s 1.0.0')

    args = parser.parse_args()
    print(f"Hello, {args.name}!")
    print("这是一个打包成 macOS 可执行文件的示例程序。")


if __name__ == '__main__':
    main()
