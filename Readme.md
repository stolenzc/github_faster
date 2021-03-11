# GitHub Faster

加快访问github的hosts文件更新脚本

主要功能是通过请求[ipaddress.com](www.ipaddress.com)来获取最快访问github的ip，然后将该ip更新到hosts文件中，来实现加快github访问

## 使用

确保计算机中安装了python3

安装依赖

```
pip3 install requests
```

执行：

Linux或MacOS系统下由于hosts文件只有root用户才有写的权限，故需要使用sudo命令执行。

```
sudo python github_faster.py
```
