## 如何上传文件到集群? / 如何从集群下载文件?
`scp`了解一下(假设账户端口为12345)

Copy local folder `/home/username/local-dir` to AI cluster directory `/home/username/`:
```
scp -P 12345 -r /home/username/local-dir root@10.15.89.41:/home/username/
```

Copy file `/home/username/project1/result.txt` from AI cluster to path `/home/username/results` on local PC:
```
scp -P 12345 root@10.15.89.41:/home/username/project1/result.txt /home/username/results/
```

## 如何查看GPU使用情况?
NVIDIA驱动提供了一个简单的命令行工具`nvidia-smi`:

```bash
# root @ piaozx.node01 in ~ [12:10:23]
$ nvidia-smi
Mon Aug 27 12:10:25 2018
+-----------------------------------------------------------------------------+
| NVIDIA-SMI 387.26                 Driver Version: 387.26                    |
|-------------------------------+----------------------+----------------------+
| GPU  Name        Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC |
| Fan  Temp  Perf  Pwr:Usage/Cap|         Memory-Usage | GPU-Util  Compute M. |
|===============================+======================+======================|
|   0  Tesla M40 24GB      Off  | 00000000:02:00.0 Off |                    0 |
| N/A   56C    P0   175W / 250W |   2657MiB / 22939MiB |     98%      Default |
+-------------------------------+----------------------+----------------------+
|   1  Tesla M40 24GB      Off  | 00000000:03:00.0 Off |                    0 |
| N/A   49C    P0   140W / 250W |    648MiB / 22939MiB |     91%      Default |
+-------------------------------+----------------------+----------------------+
|   2  Tesla M40 24GB      Off  | 00000000:83:00.0 Off |                    0 |
| N/A   55C    P0   175W / 250W |   1126MiB / 22939MiB |     98%      Default |
+-------------------------------+----------------------+----------------------+
|   3  Tesla M40 24GB      Off  | 00000000:84:00.0 Off |                    0 |
| N/A   46C    P0   142W / 250W |    648MiB / 22939MiB |     71%      Default |
+-------------------------------+----------------------+----------------------+

+-----------------------------------------------------------------------------+
| Processes:                                                       GPU Memory |
|  GPU       PID   Type   Process name                             Usage      |
|=============================================================================|
|    0     28713      C   python                                      1317MiB |
|    1     14924      C   python                                       636MiB |
|    2     16059      C   python                                      1115MiB |
|    3     19563      C   python                                       636MiB |
+-----------------------------------------------------------------------------+
```

显然, 这个工具只能显示一些基本信息, 一些你更关心的信息(谁在跑程序? 跑了多久了?)可以从[AI集群GPU Status](http://10.15.89.41:8899/gpu)获取:
![](img/gpu_status.png)


## 如何解决显存被看不见的进程占用?
用`fuser`查询是哪些进程占据了相应的显卡:
```
fuser -v /dev/nvidia*
```
之后kill掉那些进程就可以了, 多数情况都是`pytorch`的`dataloader`没有正常退出导致的


## 如何查看nvidia-driver版本? / cuda版本? / cudnn版本?
目前nvidia-driver, cuda, cudnn都集成到cuda-toolkit中了, 装机时直接到[官网](https://developer.nvidia.com/cuda-toolkit-archive)下载想要的版本即可

* 查看nvidia-driver版本
```
$ nvidia-smi | grep Version
| NVIDIA-SMI 418.74       Driver Version: 418.74       CUDA Version: 10.1     |
```
此处显示的CUDA Version并非实际安装的CUDA版本，而是当前驱动程序最高能够支持的CUDA版本。
* 查看cuda版本
```
$ cat /usr/local/cuda/version.txt
CUDA Version 9.0.176
```

* 查看cudnn版本
```
$ cat /usr/include/cudnn.h | grep "define CUDNN_MAJOR" -A 2
#define CUDNN_MAJOR 7
#define CUDNN_MINOR 1
#define CUDNN_PATCHLEVEL 4
```
即7.1.4版

## 如何查看python版本?
**查看默认Python路径** 
```
$ which python
/usr/local/bin/python
```

**查看Python版本**
```
$ python --version
Python 3.6.6
```

## 如何安装Anaconda?

如果觉得平时安装python的包太麻烦，可考虑安装Anaconda, Anaconda集成了巨大部分的python包。具体步骤如下所示(这里以Anaconda-python3.6为例):

* 下载Anaconda-python3.6. 
```
$ wget https://repo.anaconda.com/archive/Anaconda3-5.2.0-Linux-x86_64.sh
```
* 安装Anaconda
```
$ mkdir Anacondas
$ sh Anaconda3-5.2.0-Linux-x86_64.sh
```
* 在安装过程中，会让你选择Anaconda的安装路径，可以将路径改为
```
$ /root/Anacondas/anaconda3
```
* 在 zshrc 里面添加Anaconda-python路径
```
$ vim ~/.zshrc
$ export PATH="/root/Anacondas/anaconda3/bin:$PATH"  ## 在zshrc添加路径，然后保存退出
$ source ~/.zshrc

```
* 检查是否安装成功
```
$ python

Python 3.6.4 |Anaconda, Inc.| (default, Jan 16 2018, 12:04:33)
[GCC 4.2.1 Compatible Clang 4.0.1 (tags/RELEASE_401/final)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>>
```
* 可以再次查看python路径
```
$ which python
/root/Anacondas/anaconda3/bin/python
```

## 如何查看pytorch版本? / tensorflow版本?
[pytorch 官方网址](https://pytorch.org/previous-versions/)

1. 查看pytorch版本
```
$ python

Python 3.6.6 (default, Jun 28 2018, 04:42:43)
[GCC 5.4.0 20160609] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import torch
>>> print(torch.__version__)
0.3.1
```

## 如何安装指定的pytorch版本?
例如想安装0.4.0版本的pytorch, 环境是cuda-90，python3.6, 具体步骤如下所示:
```
$ pip uninstall torch
$ wget http://download.pytorch.org/whl/cu90/torch-0.4.0-cp36-cp36m-linux_x86_64.whl
$ pip install torch-0.4.0-cp36-cp36m-linux_x86_64.whl
```

检查指定版本的pytorch是否安装成功
```
$ python3
Python 3.6.4 |Anaconda, Inc.| (default, Jan 16 2018, 12:04:33)
[GCC 4.2.1 Compatible Clang 4.0.1 (tags/RELEASE_401/final)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> import torch
>>> print(torch.__version__)
0.4.0
```
## 如何指定程序在某张显卡运行:
* CUDA 自带的命令
```
$ CUDA_VISIBLE_DEVICES=0,1,2 python xxx.py ## 数字代表显卡的index
```
* 利用zsh事先定义好的function来指定显卡:
```
$ set_gpu 0,1,2
$ python xxx.py
```

## 显存被看不见的进程占据怎么办?
```
# root @ piaozx.node01 in ~ [12:10:23]
$ nvidia-smi
Mon Aug 27 12:10:25 2018
+-----------------------------------------------------------------------------+
| NVIDIA-SMI 387.26                 Driver Version: 387.26                    |
|-------------------------------+----------------------+----------------------+
| GPU  Name        Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC |
| Fan  Temp  Perf  Pwr:Usage/Cap|         Memory-Usage | GPU-Util  Compute M. |
|===============================+======================+======================|
|   0  Tesla M40 24GB      Off  | 00000000:02:00.0 Off |                    0 |
| N/A   56C    P0   175W / 250W |   2657MiB / 22939MiB |      0%      Default |
+-------------------------------+----------------------+----------------------+
|   1  Tesla M40 24GB      Off  | 00000000:03:00.0 Off |                    0 |
| N/A   49C    P0   140W / 250W |    648MiB / 22939MiB |      0%      Default |
+-------------------------------+----------------------+----------------------+
|   2  Tesla M40 24GB      Off  | 00000000:83:00.0 Off |                    0 |
| N/A   55C    P0   175W / 250W |   1126MiB / 22939MiB |      0%      Default |
+-------------------------------+----------------------+----------------------+
|   3  Tesla M40 24GB      Off  | 00000000:84:00.0 Off |                    0 |
| N/A   46C    P0   142W / 250W |    648MiB / 22939MiB |      0%      Default |
+-------------------------------+----------------------+----------------------+

+-----------------------------------------------------------------------------+
| Processes:                                                       GPU Memory |
|  GPU       PID   Type   Process name                             Usage      |
|=============================================================================|
|                                                                             |
|                                                                             |
|                                                                             |
|                                                                             |
+-----------------------------------------------------------------------------+
```

## 如何创建python的虚拟环境?


## 如何让程序在后台运行?
If you directly run come commands in your terminal, their processes will be termimated once you disconnect from AI cluster. In order to make your command stay alive after you close the terminal session, you have to make your command process run in background using `nohup command args &`. Optionally, you can specify the file where the [stdout](https://en.wikipedia.org/wiki/Standard_streams) will be redirected. Here are some examples:

```sh
# run a training scripts in the background and redirect stdout to file "out.txt"
nohup python train.py --lr 0.1 --epochs 100 >> out.txt &
```
Then you can use `tailf out.txt` to monitor your script's output. You can safely use `CTRL-C` to terminate `tailf` command without effect on your script.
If you want to terminate your command running in the background, you should first get the **process id(PID)** of your command. This can be done using `ps aux`, you will see a list of process running on the node. You can use `grep` to filter the output, like the following:

```sh
# find the PID of processes whose name containing key words "python"
ps aux | grep python
```

You will only see all process whose command line contain key words `python`.
Then, you can get your process PID in the corresponding column of the output. To terminate your command process, enter the following command:

```sh
kill -9 12345 23456
```
where `12345` and `23456` are PIDs of the processes you wish to terminate.


## 如何配置和使用screen / tmux?
### 配置tmux
* 下载tmux
```
$ apt-get install tmux
```
* 修改tmux设置，使得可以用鼠标在不同panel切换。
```
$ vi .tmux.conf
$ set-option -g mouse on  ## 保存退出
```
* tmux 常用快捷键
```
ctrl-b      ## to enter command mode.
ctrl-b + d  ## detach the session
ctrl-b + $  ## rename the session
ctrl-b + $  ## creat new window
ctrl-b + "  ## create left-right panel
ctrl-b + %  ## create up-down panel
ctrl-b + x  ## close pannel
ctrl-b + &  ## close window
tmux attach -t session-name  ## re-enter session
```

### 如何配置screen

## zsh是什么, 如何配置和使用zsh?

