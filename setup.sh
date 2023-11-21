#!/bin/bash

# 检测操作系统类型
OS=$(uname -s)
VER=$(uname -r)

echo "检测到操作系统：$OS 版本：$VER"

# 检测和安装 Python 3.8+
check_and_install_python() {
    required_version="3.8"
    if command -v python3 &>/dev/null; then
        current_version=$(python3 -c 'import platform; print(platform.python_version())')
        if [[ $(echo -e "$current_version\n$required_version" | sort -V | head -n1) = "$required_version" ]]; then
            echo "已安装 Python $current_version"
            return
        fi
    fi
    echo "正在安装 Python 3.8+ ..."
    # 根据操作系统使用不同的安装命令
    case $OS in
        Linux)
            sudo apt-get update
            sudo apt-get install -y python3 python3-pip
            ;;
        *)
            echo "不支持的操作系统: $OS"
            exit 1
            ;;
    esac
}

# 检测和安装 Docker
check_and_install_docker() {
    if ! command -v docker &>/dev/null; then
        echo "正在安装 Docker ..."
        curl -fsSL https://get.docker.com -o get-docker.sh
        sudo sh get-docker.sh
    else
        echo "已安装 Docker"
    fi
}

# 安装其他依赖
install_dependencies() {
    echo "正在安装 ffmpeg, mktorrent 和 mediainfo ..."
    sudo apt-get update
    sudo apt-get install -y ffmpeg mktorrent mediainfo
}

# 安装 pip 依赖
install_pip_dependencies() {
    if [ -f requirements.txt ]; then
        echo "安装 pip 依赖..."
        pip3 install -r requirements.txt
    else
        echo "未找到 requirements.txt"
    fi
}

# 主函数
main() {
    check_and_install_python
    check_and_install_docker
    install_dependencies
    install_pip_dependencies
    echo "环境配置完成。"
}

main
