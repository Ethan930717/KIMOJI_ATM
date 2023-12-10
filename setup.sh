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
        Darwin)
            brew install python3
            ;;
        *)
            echo "不支持的操作系统: $OS"
            echo "请手动配置环境"
            exit 1
            ;;
    esac
}

# 检测和安装 Docker
check_and_install_docker() {
    case $OS in
        Linux|Darwin)
            if ! command -v docker &>/dev/null; then
                echo "正在安装 Docker ..."
                curl -fsSL https://get.docker.com -o get-docker.sh
                sudo sh get-docker.sh
            else
                echo "已安装 Docker"
            fi
            ;;
        *)
            echo "不支持的操作系统: $OS"
            echo "请手动安装 Docker"
            exit 1
            ;;
    esac
}

# 拉取 Docker 镜像
pull_docker_images() {
    echo "正在拉取 Docker 镜像..."
    docker pull hudan717/kimoji-bdinfo
    docker pull jrottenberg/ffmpeg:ubuntu
}

# 安装其他依赖
install_dependencies() {
    case $OS in
        Linux)
            echo "正在安装mediainfo ..."
            sudo apt-get update
            sudo apt-get install -y mediainfo
            ;;
        Darwin)
            echo "正在使用 Homebrew mediainfo ..."
            brew install mediainfo
            ;;
        *)
            echo "不支持的操作系统: $OS"
            echo "请手动安装 mediainfo"
            exit 1
            ;;
    esac
}

# 安装 pip 依赖
install_pip_dependencies() {
    if [ -f requirements.txt ]; then
        echo "安装 pip 依赖..."
        pip install -r requirements.txt
    else
        echo "未找到 requirements.txt"
    fi
}

configure() {
    echo "环境已配置完成，请在config.yaml中更改您的配置信息"

    # 重命名配置文件
    sudo mv config_example.yaml config.yaml
}

# 主函数
main() {
    check_and_install_python
    check_and_install_docker
    pull_docker_images
    install_dependencies
    install_pip_dependencies
    configure
    echo "全部配置已完成。"
    sudo chmod a+x k
    sudo chmod a+x update

    ./k
}

main
