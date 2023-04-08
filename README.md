# HelloGN
[TOC]



## 1、介绍GN



## 2、安装GN

目前有两种方式

* 直接下载gn可执行文件，将文件放在`/usr/local/bin`[^2]

  下载地址，可以参考官方文档这段话[^1]，如下

  > You can download the latest version of GN binary for [Linux](https://chrome-infra-packages.appspot.com/dl/gn/gn/linux-amd64/+/latest), [macOS](https://chrome-infra-packages.appspot.com/dl/gn/gn/mac-amd64/+/latest) and [Windows](https://chrome-infra-packages.appspot.com/dl/gn/gn/windows-amd64/+/latest) from Google's build infrastructure (see “Versioning and distribution” below for how this is expected to work).

* 下载源码，自己编译

```shell
$ git clone https://gn.googlesource.com/gn
$ cd gn
$ python build/gen.py # --allow-warning if you want to build with warnings.
$ ninja -C out
ninja: Entering directory `out'
[287/287] LINK gn_unittests
```

说明

> 1. 执行`python build/gen.py`会在out文件夹生成几个文件。
>
> 2. `ninja`命令，可以通过`brew install ninja`来安装
>
> 3. 可选执行下面命令
>
>    ```shell
>    $ out/gn_unittests
>    [688/688] ImportantFileWriterTest.Basic
>    PASSED
>    ```
>
>    





## TODO

Ninja

https://ninja-build.org/



## References

[^1]:https://gn.googlesource.com/gn/+/master
[^2]:https://zhuanlan.zhihu.com/p/142169221



