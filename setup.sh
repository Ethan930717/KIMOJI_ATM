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
    docker pull iniwex/kimoji-bdinfo
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
    echo "环境已配置完成，请添加您的配置信息"

    # 输入并更新配置
    read_config() {
        local prompt=$1
        local key=$2
        local default=$3
        local input
        while true; do
            read -p "$prompt ($default): " input
            if [[ -z "$input" ]]; then
                input=$default
            fi
            if [[ "$input" == "q" ]]; then
                return 1
            else
                # 更新配置文件
                sed -i '' "s|$key:.*|$key: '$input'|" config_example.yaml
                return 0
            fi
        done
    }

    # 逐个询问并更新配置
    read_config "请输入您存放资源的主目录路径" "file_dir" "例：/root/media/movie" || return
    read_config "请输入存放种子文件的路径" "torrent_dir" "例：/root/torrent（一般人都不会有专门的种子文件夹，可以指定任意一个已经存在的文件夹，用来存放阿K制作的种子）" || return
    read_config "请输入KIMOJI用户名" "username" "阿K支持中文名注册哦" || return
    read_config "请输入KIMOJI登陆密码" "password" "password" || return
    read_config "请输入qb路径" "url" "例：192.168.1.1" || return
    read_config "请输入qb端口" "port" "例：8080" || return
    read_config "请输入qb登陆账号" "username" "例：admin" || return
    read_config "请输入qb登陆密码" "password" "例：adminadmin" || return
    read_config "请输入qb保存路径" "save_path" "例：/download" || return

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
