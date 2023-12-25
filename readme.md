# KIMOJI_ATM 使用指南

阿K专属发种机，用于简化在KIMOJI的发种过程，把PT玩家们机器上保的种自动按照KIMOJI的要求进行发种。

## 使用方式

### ubuntu debian macos用户，可以直接使用一键配置脚本进行环境的配置

* 步骤 1: 克隆仓库

* `git clone https://github.com/Ethan930717/KIMOJI_ATM
`
* 步骤 2: 添加权限

`chmod a+x setup.sh
`
* 步骤 3: 加载自动配置

`./setup.sh
`
### unraid请先在应用市场安装python，nerdtools插件，然后在nerdtools中找到mediainfo进行安装

*  克隆

* `pip install -r requirements.txt 或 pip3 install -r requirements.txt` 安装依赖

* `mv config_example.yaml config.yaml` 重命名配置文件，随后进入config.yaml手动编辑配置信息

* `sudo chmod a+x k` 为启动指令赋权

* `./k` 召唤阿K


