# HelloGN
[TOC]



## 1、介绍GN

GN是Chromium、Fuchsia等工程使用的编译系统，它可以生成C/C++、Rust、Objective-C、Swift等对应的Ninja编译文件。

参考官方文档描述[^1]，如下

> GN is currently used as the build system for Chromium, Fuchsia, and related projects.
>
> GN can generate Ninja build files for C, C++, Rust, Objective C, and Swift source on most popular platforms. 

实际上，GN针对Ninja的编译系统，然后使用Ninja编译生成可执行文件。

官方文档对GN的定义[^1]，如下

> GN is a meta-build system that generates build files for [Ninja](https://ninja-build.org/).

我猜测，GN是Generate Ninja的缩写。

说明

> 1. [GN主页](https://gn.googlesource.com/gn/+/master)
> 2. [GN手册](https://gn.googlesource.com/gn/+/main/docs/reference.md)
> 3. GN的[QuickStart](https://gn.googlesource.com/gn/+/main/docs/quick_start.md)
> 4. GN的[Q&A](https://gn.googlesource.com/gn/+/main/docs/faq.md)



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

完成上面的编译，在out文件夹下，会有gn可执行文件



### (1) 第一个GN编译的程序

在GN仓库的examples文件夹中提供一些源文件，用于测试GN编译。找到`gn/examples/simple_build/tutorial/tutorial.cc`这个文件，它的内容如下

```c
#include <stdio.h>

int main(int argc, char* argv[]) {
  printf("Hello from the tutorial.\n");
  return 0;
}
```

参考官方的QuickStart文档[^3]，下面学习如何使用GN



#### a. 添加`BUILD.gn`文件

在tutorial.cc所在文件夹下，添加`BUILD.gn`文件，内容如下

```javascript
executable("tutorial") {
  sources = [
    "tutorial.cc",
  ]
}
```

在`gn/examples/simple_build/`找到BUILD.gn文件，没有则创建一个，内容如下

```javascript
group("tools") {
  deps = [
    # This will expand to the name "//tutorial:tutorial" which is the full name
    # of our new target. Run "gn help labels" for more.
    "//tutorial",
  ]
}
```

说明

> 1. BUILD.gn文件中，有其他配置，可以暂时注释掉
> 2. `"//tutorial"`属于label写法，相当于`//tutorial:tutorial`，意思是在tutorial文件夹下找到BUILD.gn，然后在该文件中找到`tutorial`target。

上面创建一个组，用于管理编译依赖，官方文档对group的描述[^3]，如下

> In GN, a “group” is just a collection of dependencies that’s not complied or linked



#### b. 使用GN编译

由于采用依赖编译，使用simple_build文件夹下面的BUILD.gn文件，那么cd到simple_build文件夹，执行下面命令，如下

```shell
$ ../../out/gn gen out
$ ninja -C out tutorial
$ ./out/tutorial 
Hello from the tutorial.
```

到这里为止，第一个简单的GN编译的程序完成。

这里简单总结下步骤

* 编写BUILD.gn文件，可能有多个
* 使用`gn`命令，生成Ninja编译文件
* 使用`ninja`命令，生成可执行文件
* 执行可执行文件



### (2) GN编译静态库和动态库

在simple_build文件夹下面的BUILD.gn文件，已经写好两个target，分别是静态库和动态库。如下

```javascript
shared_library("hello_shared") {
  sources = [
    "hello_shared.cc",
    "hello_shared.h",
  ]

  defines = [ "HELLO_SHARED_IMPLEMENTATION" ]
}

static_library("hello_static") {
  sources = [
    "hello_static.cc",
    "hello_static.h",
  ]
}
```

这里defines字段定义的预处理器宏，如果有有多个，可以按照下面格式

```javascript
defines = [
  "HELLO_SHARED_IMPLEMENTATION",
  "ENABLE_DOOM_MELON=0",
]
```

可执行文件hello，依赖hello_shared和hello_static，配置如下

```javascript
executable("hello") {
  sources = [ "hello.cc" ]

  deps = [
    ":hello_shared",
    ":hello_static",
  ]
}
```

下面编译生成可执行文件hello

```shell
$ ninja -C out hello
ninja: Entering directory `out'
[0/1] Regenerating ninja files
[6/6] LINK hello
$ out/hello
Hello, world
```

这个例子中没有运行`gn`命令，实际自动运行gn，重新生成ninja编译文件，参考输出Regenerating ninja files



### (3) 从0创建GN工程

本文的步骤大概参考这篇文章[^9]，略有一些不同。

说明

> 这篇文章[^10]也是很好入门创建GN工程，内容和本文是差不多的。



#### a. 将gn命令导入shell中

由于gn命令是编译出来的可执行文件，这里将gn命令导入zsh中，配置`.zshrc`，如下

```shell
export PATH="$PATH:$HOME/GitHub_Projects/HelloGN/gn/out"
```



#### b. 创建gn工程

```shell
$ tree -a .
.
├── .gn
├── BUILD.gn
├── build
│   ├── BUILDCONFIG.gn
│   └── toolchains
│       └── BUILD.GN
└── main.cpp

2 directories, 5 files
```

简单gn工程的模板，可以参考上面的结构。下面会一一介绍这些配置文件。

说明

> 1. gn工程的`.gitignore`，可以直接参考gn仓库的`.gitignore`，不用自己手动写
> 2. 用于编译的配置，都放在build文件夹下面



#### c. `.gn`文件

`.gn`文件是根目录配置文件，一般很简单内容，如下

```properties
buildconfig = "//build/BUILDCONFIG.gn"
```

上面用于指定gn命令从哪里读取配置，这里指定的路径是相对于根目录的`build/BUILDCONFIG.gn`



#### d. `build/BUILDCONFIG.gn`文件

`BUILDCONFIG.gn`文件是gn命令读取的配置文件。

```properties
if (target_os == "") {
  target_os = host_os
}
if (target_cpu == "") {
  target_cpu = host_cpu
}
if (current_cpu == "") {
  current_cpu = target_cpu
}
if (current_os == "") {
  current_os = target_os
}

is_linux = host_os == "linux" && current_os == "linux" && target_os == "linux"
is_mac = host_os == "mac" && current_os == "mac" && target_os == "mac"

set_default_toolchain("//build/toolchains:gcc")
```

这里参考官方gn仓库的examples文件夹下的simple_build例子使用的`BUILDCONFIG.gn`文件。它的位置是`gn/examples/simple_build/build/BUILDCONFIG.gn`



#### e. `build/toolchains/BUILD.gn`文件

这里`BUILD.gn`文件不同于其他地方的`BUILD.gn`文件，主要配置编译工具，如下

```properties
# Copyright 2014 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

toolchain("gcc") {
  tool("cc") {
    depfile = "{{output}}.d"
    command = "gcc -MMD -MF $depfile {{defines}} {{include_dirs}} {{cflags}} {{cflags_c}} -c {{source}} -o {{output}}"
    depsformat = "gcc"
    description = "CC {{output}}"
    outputs =
        [ "{{source_out_dir}}/{{target_output_name}}.{{source_name_part}}.o" ]
  }

  tool("cxx") {
    depfile = "{{output}}.d"
    command = "g++ -MMD -MF $depfile {{defines}} {{include_dirs}} {{cflags}} {{cflags_cc}} -c {{source}} -o {{output}}"
    depsformat = "gcc"
    description = "CXX {{output}}"
    outputs =
        [ "{{source_out_dir}}/{{target_output_name}}.{{source_name_part}}.o" ]
  }

  tool("alink") {
    command = "rm -f {{output}} && ar rcs {{output}} {{inputs}}"
    description = "AR {{target_output_name}}{{output_extension}}"

    outputs =
        [ "{{target_out_dir}}/{{target_output_name}}{{output_extension}}" ]
    default_output_extension = ".a"
    output_prefix = "lib"
  }

  tool("solink") {
    soname = "{{target_output_name}}{{output_extension}}"  # e.g. "libfoo.so".
    sofile = "{{output_dir}}/$soname"
    rspfile = soname + ".rsp"
    if (is_mac) {
      os_specific_option = "-install_name @executable_path/$sofile"
      rspfile_content = "{{inputs}} {{solibs}} {{libs}}"
    } else {
      os_specific_option = "-Wl,-soname=$soname"
      rspfile_content = "-Wl,--whole-archive {{inputs}} {{solibs}} -Wl,--no-whole-archive {{libs}}"
    }

    command = "g++ -shared {{ldflags}} -o $sofile $os_specific_option @$rspfile"

    description = "SOLINK $soname"

    # Use this for {{output_extension}} expansions unless a target manually
    # overrides it (in which case {{output_extension}} will be what the target
    # specifies).
    default_output_extension = ".so"

    # Use this for {{output_dir}} expansions unless a target manually overrides
    # it (in which case {{output_dir}} will be what the target specifies).
    default_output_dir = "{{root_out_dir}}"

    outputs = [ sofile ]
    link_output = sofile
    depend_output = sofile
    output_prefix = "lib"
  }

  tool("link") {
    outfile = "{{target_output_name}}{{output_extension}}"
    rspfile = "$outfile.rsp"
    if (is_mac) {
      command = "g++ {{ldflags}} -o $outfile @$rspfile {{solibs}} {{libs}}"
    } else {
      command = "g++ {{ldflags}} -o $outfile -Wl,--start-group @$rspfile {{solibs}} -Wl,--end-group {{libs}}"
    }
    description = "LINK $outfile"
    default_output_dir = "{{root_out_dir}}"
    rspfile_content = "{{inputs}}"
    outputs = [ outfile ]
  }

  tool("stamp") {
    command = "touch {{output}}"
    description = "STAMP {{output}}"
  }

  tool("copy") {
    command = "cp -af {{source}} {{output}}"
    description = "COPY {{source}} {{output}}"
  }
}
```

上面的内容也是参考官方gn仓库的examples文件夹下的simple_build例子使用的`BUILD.gn`文件。它的位置是`gn/examples/simple_build/build/toolchain/BUILD.gn`。具体语法这里不做介绍。

说明

> 这里的`BUILD.gn`使用到在`BUILDCONFIG.gn`中定义的变量is_mac



#### f. `BUILD.gn`文件

应用程序或者静态/动态库的编译文件，也是命名为`BUILD.gn`文件，这里编译一个可执行文件hello，使用main.cpp作为源文件。

```properties
executable("hello") {
  sources = [
    "main.cpp",
  ]
}
```

说明

> 一般来说，配置好gn工程，后续维护都在这个`BUILD.gn`文件，其他配置文件不会经常改动。



main.cpp内容，如下

```cpp
#include <iostream>

using namespace std;

int main(int argc, const char * argv[]) {
    std::cout << "Hello, World!" << std::endl;
    return 0;
}
```



#### g. 生成配置并编译

完成上面的配置，组合使用gn和ninja命令，如下

```shell
$ gn gen out  
Done. Made 1 targets from 3 files in 5ms
$ ninja -C out
ninja: Entering directory `out'
[2/2] LINK hello
$ out/hello 
Hello, World!
```

说明

> 1. 没有生成out文件夹，需要使用gn来生成，out文件夹主要包含ninja的编译配置文件和编译输出的产物
> 2. 如果gn命令使用过，后续编译可以直接使用ninja命令
> 3. out文件夹一般无需提交到git仓库，也可以随时清理，然后重新编译







https://blog.simplypatrick.com/posts/2016/01-23-gn/



## 3、GN语法

在上面BUILD.gn文件中已经看到GN语法，完整的编写语法，可以参考官方这篇文档[^4]。

GN语法是一个简单的编程语言，了解C的开发者都容易理解它的语法。

官方设计哲学，如下

> Design philosophy
>
> - Writing build files should not be a creative endeavour. Ideally two people should produce the same buildfile given the same requirements. There should be no flexibility unless it's absolutely needed. As many things should be fatal errors as possible.
> - The definition should read more like code than rules. I don't want to write or debug Prolog. But everybody on our team can write and debug C++ and Python.
> - The build language should be opinionated as to how the build should work. It should not necessarily be easy or even possible to express arbitrary things. We should be changing source and tooling to make the build simpler rather than making everything more complicated to conform to external requirements (within reason).
> - Be like Blaze when it makes sense (see “Differences and similarities to Blaze” below).

这里简单归纳几点

* 编写编译文件不是什么创新的事情，因此GN语法不应该太灵活，尽可能产生错误
* GN语法应该像代码而不是规则，不应该需要调试GN代码
* GN编译语言应该是直观的，而不是编写复杂的编译代码
* 有点像Blaze

了解上面设计哲学，方便理解GN语法有些能力支持，有些能力却不支持，甚至明确不会支持，而是采用报错提示。

GN语言的数据类型，有下面几种

* Boolean，`true`和`false`
* 64位有符号整数
* 字符串Strings
* 列表Lists
* 字典Scopes

官方文档定义，如下

> The types are:
>
> - Boolean (`true`, `false`).
> - 64-bit signed integers.
> - Strings.
> - Lists (of any other types).
> - Scopes (sort of like a dictionary, only for built-in stuff).

说明

> 使用`gn help grammar`可以查询完整的GN语法



### (1) Strings

使用双引号`"`表示字符串，使用`\`做转义符。仅能支持的转义，如下

* `\"`，转义引号
* `\$`，转义$符号
* `\\`，转义`\`符号

其他形式反斜杠都表示字面的反斜杠，举个例子`"C:\foo\bar.h"`中不会认为`\b`是转义的。

使用`$`进行变量替换，也可选的使用`${var}`形式。举个例子，如下

```properties
a = "mypath"
b = "$a/foo.cc"  # b -> "mypath/foo.cc"
c = "foo${a}bar.cc"  # c -> "foomypathbar.cc"
```



### (2) Lists

列表不能获取长度，判断是否空的列表，可以采用`a == []`方式。

列表支持几种操作

* 追加元素
* 移除元素
* 添加另一个list中的所有元素
* 下标获取特定的元素

举个例子，如下

```properties
# append elements
a = [ "first" ]
a += [ "second" ]  # [ "first", "second" ]
a += [ "third", "fourth" ]  # [ "first", "second", "third", "fourth" ]
b = a + [ "fifth" ]  # [ "first", "second", "third", "fourth", "fifth" ]

# remove elements
a = [ "first", "second", "third", "first" ]
b = a - [ "first" ]  # [ "second", "third" ]
a -= [ "second" ]  # [ "first", "third", "first" ]

# get element by index
a = [ "first", "second", "third" ]
b = a[1]  # -> "second"
```

注意

* 下标获取元素是只读的，不能使用下标写入元素，例如`a[1] = "something"`
* 不能直接覆盖非空list，会认为是错误的。但是使用空的列表覆盖。

举个例子，如下

```properties
a = [ "one" ]
a = [ "two" ]  # Error: overwriting nonempty list with a nonempty list.
a = []         # OK
a = [ "two" ]  # OK
```

上面想用two替换one，不能直接赋值，而是先用空的列表赋值，然后再用two赋值。



### (3) Conditionals

条件语句和C是一样的。举个例子，如下

```c
  if (is_linux || (is_win && target_cpu == "x86")) {
    sources -= [ "something.cc" ]
  } else if (...) {
    ...
  } else {
    ...
  }
```



### (4) Looping

循环语句使用foreach。举个例子，如下

```c
foreach(i, mylist) {
  print(i)  # Note: i is a copy of each element, not a reference to it.
}
```



### (5) Function calls

函数调用和C一样。举个例子，如下

```c
print("hello, world")
assert(is_win, "This should only be executed on Windows")
```

注意

> 函数都是内置的，用户不能定义函数

某些函数可以带闭包。举个例子，如下

```c
static_library("mylibrary") {
  sources = [ "a.cc" ]
}
```



### (6) Scoping and execution

Scoping是指文件中，或函数调用，使用`{ }`。类似C的作用域。



### (7) 文件和文件夹命名

文件和文件夹命名都是字符串，有三种形式

* 相对路径 (Relative names)

```c
"foo.cc"
"src/foo.cc"
"../src/foo.cc"
```

* source根目录路径 (Source-tree absolute names)

```c
"//net/foo.cc"
"//base/test/foo.cc"
```

* 系统绝对路径 (System absolute names)

```c
"/usr/local/include/"
"/C:/Program Files/Windows Kits/Include"
```



### (8) 编译配置

#### a. Targets

官方文档对target定义[^4]，如下

> A target is a node in the build graph. It usually represents some kind of executable or library file that will be generated. Targets depend on other targets. 

target类型，有下面一些

> - `action`: Run a script to generate a file.
> - `action_foreach`: Run a script once for each source file.
> - `bundle_data`: Declare data to go into a Mac/iOS bundle.
> - `create_bundle`: Creates a Mac/iOS bundle.
> - `executable`: Generates an executable file.
> - `group`: A virtual dependency node that refers to one or more other targets.
> - `shared_library`: A .dll or .so.
> - `loadable_module`: A .dll or .so loadable only at runtime.
> - `source_set`: A lightweight virtual static library (usually preferrable over a real static library since it will build faster).
> - `static_library`: A .lib or .a file (normally you'll want a `source_set` instead).

说明

> 使用`gn help <targettype>`可以查询上面每种target类型的具体信息



在template中，可以下面类型target

> - `component`: Either a source set or shared library, depending on the build type.
> - `test`: A test executable. On mobile this will create the appropriate native app type for tests.
> - `app`: Executable or Mac/iOS application.
> - `android_apk`: Make an APK. There are a *lot* of other Android ones, see `//build/config/android/rules.gni`.



#### b. Configs

官方文档对config定义[^4]，如下

> Configs are named objects that specify sets of flags, include directories, and defines. They can be applied to a target and pushed to dependent targets.

定义一个config。举个例子，如下

```c
config("myconfig") {
  includes = [ "src/include" ]
  defines = [ "ENABLE_DOOM_MELON" ]
}
```

使用config对象，如下

```c
executable("doom_melon") {
  configs = [ ":myconfig" ]
}
```

一般来说，每个target类型，可能有默认的config，因此使用`configs += ":myconfig"`更好。

说明

> 使用`gn help config`了解更多信息。



##### Public configs

当target A依赖另一个target B时，在target B的配置中使用public_configs字段，用于向target A输出配置。

举个例子[^5]，如下

```c
config("icu_dirs") {
  include_dirs = [ "include" ]
}
shared_library("icu") {
  public_configs = [ ":icu_dirs" ]
}
executable("doom_melon") {
  deps = [
    # Apply ICU’s public_configs.
	  ":icu",
  ]
}
```

除了使用`public_configs`字段，`public_deps`字段结合`public_configs`字段，可以间接输出配置。

举个例子[^5]，如下

```c
shared_library("i18n_utils") {
  ...
  public_deps = [
    "//third_party/icu",
  ] 
}
executable("doom_melon") {
  deps = [
    # Apply ICU’s public_configs.
    ":i18n_utils",
  ]
}
```

上面的依赖关系是，doom_melon > i18n_utils > icu，当编译doom_melon，需要icu的public_configs配置，使用public_deps字段，相当于把icu暴露给doom_melon使用。





#### c. Templates

Templates是GN复用代码的方式。Templates可以展开成多个target类型。

举个例子，如下

```c
# Declares a script that compiles IDL files to source, and then compiles those
# source files.
template("idl") {
  # Always base helper targets on target_name so they're unique. Target name
  # will be the string passed as the name when the template is invoked.
  idl_target_name = "${target_name}_generate"
  action_foreach(idl_target_name) {
    ...
  }

  # Your template should always define a target with the name target_name.
  # When other targets depend on your template invocation, this will be the
  # destination of that dependency.
  source_set(target_name) {
    ...
    deps = [ ":$idl_target_name" ]  # Require the sources to be compiled.
  }
}
```

使用idl模板，相当于创建一个模板实例，如下

```c
import("//tools/idl_compiler.gni")

idl("my_interfaces") {
  sources = [ "a.idl", "b.idl" ]
}
```

采用`invoker`变量获取，模板实例中的数据，举个例子，如下

```c
template("idl") {
  source_set(target_name) {
    sources = invoker.sources
  }
}
```





## 4、Ninja

Ninja是小型的编译系统，它有两个特点：

* Ninja的编译配置，可以由更高级的编译系统生成
* Ninja尽可能运行编译

参考官方文档的描述[^6]，如下

> Ninja is a small build system with a focus on speed. It differs from other build systems in two major respects: it is designed to have its input files generated by a higher-level build system, and it is designed to run builds as fast as possible.

能生成Ninja的编译配置的系统，称为meta-build system。目前有下面几种[^7]

* gn
* CMake
* [其他](https://github.com/ninja-build/ninja/wiki/List-of-generators-producing-ninja-build-files)

说明

> 1. Ninja的GitHub地址在[这里](https://github.com/ninja-build/ninja)
> 2. Ninja的使用手册在[这里](https://ninja-build.org/manual.html)



### (1) 安装Ninja

在MacOS上使用Homebrew安装[^8]，如下

```shell 
$ brew install ninja
```



### (2) 使用Ninja

TODO

https://blog.simplypatrick.com/posts/2012/08-18-ninja-a-small-build-system/





## References

[^1]:https://gn.googlesource.com/gn/+/master
[^2]:https://zhuanlan.zhihu.com/p/142169221

[^3]:https://gn.googlesource.com/gn/+/main/docs/quick_start.md
[^4]:https://gn.googlesource.com/gn/+/main/docs/language.md
[^5]:https://docs.google.com/presentation/d/15Zwb53JcncHfEwHpnG_PoIbbzQ3GQi_cpujYwbpcbZo/edit#slide=id.g119d702868_0_12
[^6]:https://ninja-build.org/
[^7]:https://ninja-build.org/manual.html
[^8]:https://blog.simplypatrick.com/posts/2012/08-18-ninja-a-small-build-system/

[^9]:https://www.topcoder.com/thrive/articles/Introduction%20to%20Build%20Tools%20GN%20&%20Ninja
[^10]:https://blog.simplypatrick.com/posts/2016/01-23-gn/



