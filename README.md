# HelloGN
[TOC]



## 1、介绍GN

GN是Chromium、Fuchsia等工程使用的编译系统，它可以生成C/C++、Rust、Objective-C、Swift等对应的Ninja编译文件。

参考官方文档描述[^1]，如下

> GN is currently used as the build system for Chromium, Fuchsia, and related projects.
>
> GN can generate Ninja build files for C, C++, Rust, Objective C, and Swift source on most popular platforms. 

实际上，GN是针对Ninja的元编译系统，然后使用Ninja编译生成文件（可执行文件等）。

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
> 2. `"//tutorial"`属于label写法，相当于`//tutorial:tutorial`，意思是在tutorial文件夹下找到BUILD.gn，然后在该文件中找到名为`tutorial`的target。

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

> 如果不想使用官方仓库的simple_build例子，可以参考HelloWorld工程



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

这个例子中没有运行`gn`命令，实际上会自动运行gn，重新生成ninja编译文件，因为有输出Regenerating ninja files的提示。



### (3) 从0创建GN工程

上面已经介绍如何使用GN，但是都是从官方example工程中直接使用的。这里介绍如何从0创建GN工程，本文的步骤大概参考这篇文章[^9]，略有一些不同。

说明

> 这篇文章[^10]也是很好入门创建GN工程，内容和本文是差不多的。



#### a. 将gn命令导入shell环境中

由于gn命令是编译出来的可执行文件，为了使用方便，可以导入shell环境中。这里将gn命令导入zsh中，配置`.zshrc`，如下

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

上面是简单的gn工程模板。下面会一一介绍这些配置文件。

说明

> 1. gn工程的`.gitignore`，可以直接参考gn仓库的`.gitignore`，不用自己手动写
> 2. 用于编译的配置文件，参考官方的做法，都放在build文件夹下面。实际上，build文件夹也可以命名为其他名字。



#### c. `.gn`文件

`.gn`文件是工程，根目录配置文件，一般很简单内容，如下

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

`BUILDCONFIG.gn`是GN入口配置文件，它的作用是[^11]

> \# This is the master GN build configuration. This file is loaded after the
\# build args (args.gn) for the build directory and after the toplevel ".gn"
\# file (which points to this file as the build configuration).
\#
\# This file will be executed and the resulting context will be used to execute
\# every other file in the build. So variables declared here (that don't start
\# with an underscore) will be implicitly global.

`BUILDCONFIG.gn`会在加载`args.gn`和`.gn`之后再加载，而且每次执行文件build，都会使用这个文件提供context，因此可以在该文件定义全局变量。



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

使用idl模板（后缀名为`.gni`），相当于创建一个模板实例，如下

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

TODO: https://chromium.googlesource.com/chromium/src/build/+/refs/heads/main/docs/writing_gn_templates.md



## 4、GN手册

GN手册[^7]主要分为下面几个部分

* gn命令参数(Command)
* Target声明(Target declarations)。例如action、executable、shared_library等
* 内置函数(Buildfile functions)。例如print等
* 内置预定义变量。例如current_cpu等
* 需用户设置的变量。例如cflags等
* 其他话题

本文就按照上面结构来介绍



### (1) gn命令参数(Command)

gn命令参数，有下面几个

```shell
$ gn help
	analyze: Analyze which targets are affected by a list of files.
  args: Display or configure arguments declared by the build.
  check: Check header dependencies.
  clean: Cleans the output directory.
  clean_stale: Cleans the stale output files from the output directory.
  desc: Show lots of insightful information about a target or config.
  format: Format .gn files.
  gen: Generate ninja files.
  help: Does what you think.
  ls: List matching targets.
  meta: List target metadata collection results.
  outputs: Which files a source/target make.
  path: Find paths between two targets.
  refs: Find stuff referencing a target or file.
```

#### a. analyze

analyze用于分析某个target会被哪些文件影响。

命令格式如下

```shell
$ gn analyze <out_dir> <input_path> <output_path>
```

* out_dir，是out文件夹的路径
* input_path，是输入参数的JSON文件。例如test_targets字段是数组，包含需要检测的target
* output_path，是输出文件

TODO



#### b. args

args用于显示和配置参数。

命令格式如下

```shell
$ gn args <out_dir> [--list] [--short] [--args] [--overrides-only]
```

常见的几种用法，如下



##### 打开args.gn文件

```shell
$ gn args <out_dir>
```



##### 显示args参数

```shell
$ gn args <out_dir> --list[=<exact_arg>] [--short] [--overrides-only] [--json]
```

举个例子，如下

```shell
$ cd HelloWorld
$ gn args out --list
current_cpu
    Current value (from the default) = ""
      (Internally set; try `gn help current_cpu`.)

current_os
    Current value (from the default) = ""
      (Internally set; try `gn help current_os`.)

host_cpu
    Current value (from the default) = "x64"
      (Internally set; try `gn help host_cpu`.)

host_os
    Current value (from the default) = "mac"
      (Internally set; try `gn help host_os`.)

target_cpu
    Current value (from the default) = ""
      (Internally set; try `gn help target_cpu`.)

target_os
    Current value (from the default) = ""
      (Internally set; try `gn help target_os`.)
      
$ gn args out --list --short
current_cpu = ""
current_os = ""
host_cpu = "x64"
host_os = "mac"
target_cpu = ""
target_os = ""
```



#### c. check

TODO



#### d. clean

clean用于清理out文件夹下面的内容，但是不会删除args.gn以及ninja部分文件。

命令格式，如下

```shell
$ gn clean <out_dir>...
```

官方文档描述[^7]，如下

> Deletes the contents of the output directory except for args.gn and
>   creates a Ninja build environment sufficient to regenerate the build.



举个例子，如下

```shell
$ cd HelloWorld
$ tree out
out
├── Debug
├── args.gn
├── build.ninja
├── build.ninja.d
├── build.ninja.stamp
├── hello
├── obj
│   ├── hello.main.o
│   └── hello.ninja
└── toolchain.ninja

2 directories, 8 files
$ gn clean out
$ tree out    
out
├── args.gn
├── build.ninja
└── build.ninja.d

0 directories, 3 files
```



#### e. clean_stale

clean_stale用于过期的文件。

命名格式，如下

```shell
$ gn clean_stale [--ninja-executable=...] <out_dir>...
```

官方文档描述[^7]，如下

> Removes the no longer needed output files from the build directory and prunes
> their records from the ninja build log and dependency database. These are
> output files that were generated from previous builds, but the current build
> graph no longer references them.
>
> This command requires a ninja executable of at least version 1.10.0. The
> executable must be provided by the --ninja-executable switch.



### (2) Target声明(Target declarations)

TODO



### (3) 内置函数(Buildfile functions)

TODO



### (4) 内置预定义变量

TODO



### (5) 需用户设置的变量

TODO



### (6) 其他话题

#### a. buildargs（编译参数）

buildargs的定义，如下

> Build arguments are variables passed in from outside of the build that build
> files can query to determine how the build works.

这里的Build arguments，是指从外部传给build file的参数。有两种方式，如下

* 编辑`args.gn`文件。在out文件下直接编辑该文件，或者使用`gn args out`唤起编辑器来编辑

* `gn gen out`命令行传`--args`参数。例如

  ```shell
  $ gn gen out/FooBar --args="enable_doom_melon=true os=\"android\""
  ```

  该命令也会将参数写入到`args.gn`文件中



#### b. Build graph and execution overview

GN的完整编译流，分为六个步骤，如下

1）寻找`.gn`文件，它所在的文件夹设置为source root，并解析这个文件，确定build config文件的位置

2）执行build config文件，设置全局变量和默认toolchain名字。在这个build config文件中的任意argument、variable和default，都是对所有文件可见的

3）加载//BUILD.gn文件，它位于source root下面

4）递归地执行//BUILD.gn中的rule，如果有依赖关系，则加载其他文件夹的BUILD.gn文件。如果没有其他BUILD.gn文件，则根据`.gn`文件中secondary_source字段再搜索

5）每当一个target的依赖全部处理完，则写入`.ninja`文件到out文件夹

6）当所有target处理完，则写入`build.ninja`文件到out文件夹

根据上面的描述，GN的编译流实际是根据//BUILD.gn中设置的target及其依赖，形成一个有向无循环图。



#### c. GN语言









## 5、GN配置文件模板

使用GN可以配置各个编译工具链，实际上这些工具链的配置，根据各个平台，大部分是一样的，因此有人提供了一套配置文件，git仓库是https://github.com/timniederhausen/gn-build

这里介绍如何使用gn-build的测试工程。

* 将gn-build切到testsrc分支，获取作者的测试代码，并拷贝到UseGNBuildTest文件夹下

* 配置软链接，如下

  ```shell
  $ cd UseGNBuildTest
  $ ln -s ../gn-build build
  ```

  这里会创建一个软链接文件夹，指向本地的gn-build仓库

* 执行编译命令

  ```shell
  $ cd UseGNBuildTest
  $ gn gen out
  $ ninja -C out
  ```

说明

> 这里创建软链接的目的是
>
> * 共享gn-build仓库，不然每个GN工程下面需要一份gn-build
> * `.gn`文件中配置`buildconfig = "../gn-build/config/BUILDCONFIG.gn"`这种向外层引用的方式，执行`gn gen out`会报错

> 示例工程，见UseGNBuildTest



## 6、Ninja

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

参考官方文档[^7]可以了解如何使用Ninja，以及`build.ninja`的语法。

运行`ninja`命令，默认会在当前目录下查找`build.ninja`文件，并且编译所有过期的targets。也可以指定特定的target。

举个`build.ninja`的例子，如下

```shell
cflags = -Wall

rule cc
  command = gcc $cflags -c $in -o $out

build foo.o: cc foo.c
```

在`build.ninja`文件中，支持build语句和rule语句。

* rule语句，用于设置短名称，简化很长的命令行，例如上面的cc rule，实际对应是`gcc $cflags -c $in -o $out`命令行
* build语句，用于描述如何使用rule来编译target（也称为output文件）

官方描述Ninja会生成一个关于输入文件和输出文件的有向图，`build.ninja`文件的内容就描述这个有向图。

* rule语句，描述如何产生有向图中的边，即输入文件和输出文件
* build语句，描述工程中的依赖关系，我推测类似多个`.o`文件链接成一个可执行文件，那么这个build语句描述的是这个可执行文件依赖多个`.o`文件

官方文档的描述[^7]，如下

> Ninja evaluates a graph of dependencies between files, and runs whichever commands are necessary to make your build target up to date as determined by file modification times. If you are familiar with Make, Ninja is very similar.
>
> Conceptually, `build` statements describe the dependency graph of your project, while `rule` statements describe how to generate the files along a given edge of the graph.

了解上面的设计概念，有助于理解`build.ninja`核心语法，build语句和rule语句。



#### a. 变量

`build.ninja`中可以定义变量，在上面的例子中，如下

```shell
cflags = -Wall

rule cc
  command = gcc $cflags -c $in -o $out
```

变量的引用在等号的右边，使用`$`符号作为前缀，也可以使用花括号的形式，例如${in}。

这里定义了自定义变量cflags。

说明

> Ninja也提供内置变量，例如上面in变量和out变量，不同于自定义的变量cflags



#### b. rule语句

rule语句用于设置短名称的命令行，以`rule <name>`格式单独一行，后面跟着多行类似`variable = value`的格式。

这里的variable是Ninja提供的内置变量，例如上面例子中command变量，不需要$符号。而在value部分，也有内置变量，例如上面例子中的in变量和out变量。

Ninja的内置变量，可以参考下面这个表格，更多详细内容，参考官方文档[^7]

| 变量名                   | 作用                                             |
| ------------------------ | ------------------------------------------------ |
| command (required)       | 需要运行的命令行。每个rule仅包含一个command声明  |
| depfile                  |                                                  |
| msvc_deps_prefix         |                                                  |
| description              | command的描述。使用`-v`运行ninja，会打印这个描述 |
| dyndep                   |                                                  |
| generator                |                                                  |
| in                       | 空格分隔的输入文件列表                           |
| in_newline               | 和in一样，但是使用换行符作为分隔                 |
| out                      | 空格分隔的输出文件列表                           |
| restat                   |                                                  |
| rspfile, rspfile_content |                                                  |



#### c. build语句

build语句描述输入文件和输出文件的关系。它以build关键词开头，格式是`build outputs: rulename inputs`。这个声明描述的是所有输出文件来源自输入文件，当输入文件缺失或者发生变更时，Ninja执行rule会重新生成这些输出文件。

build语句后面可以跟着一组key = value，用于修改rule语句中的变量。举个例子，如下

```shell
cflags = -Wall -Werror
rule cc
  command = gcc $cflags -c $in -o $out

# If left unspecified, builds get the outer $cflags.
build foo.o: cc foo.c

# But you can shadow variables like cflags for a particular build.
build special.o: cc special.c
  cflags = -Wall

# The variable was only shadowed for the scope of special.o;
# Subsequent build lines get the outer (original) cflags.
build bar.o: cc bar.c
```

上面有三个build语句，在第二个build语句后面，修改了cflags变量的值，而且仅对第二个build语句产生效果。第一个和第三个build语句，都使用原始的cflags变量的值。



#### d. phony rule

phony rule是内置的rule，类似上面自定义cc rule，但不需要使用rule声明。

官方文档[^7]使用phony rule，做一些特殊用途

* 创建target别名
* 创建dummy target



创建target别名，适用于target名字比较长的情况。举个例子，如下

```shell
cflags = -Wall

rule cc
  command = gcc $cflags -c $in -o $out

build some/file/in/a/faraway/subdir/foo.o: cc some/file/in/a/faraway/subdir/foo/foo.c
build foo: phony some/file/in/a/faraway/subdir/foo.o
```

`some/file/in/a/faraway/subdir/foo.o`名字比较长，使用phony rule重新创建一个名为foo的target，当执行下面命令

```shell
$ ninja foo
```

实际会执行第一个build语句。

> 示例见02_syntax_phony_alias



创建dummy target，和创建别名实际是一样的。举个例子，如下

```shell
rule touch
  command = touch $out
build file_that_always_exists.dummy: touch
build dummy_target_to_follow_a_pattern: phony file_that_always_exists.dummy
```

这里touch rule没有输入文件。

> 示例见02_syntax_phony_dummy_target



#### e. default taget语句

没有default target语句时，执行ninja命令，会默认把所有target执行一遍。使用default关键词可以指定哪些target作为默认执行。

举个例子，如下

```shell
rule touch
  command = touch $out

build foo: touch
build bar: touch
build baz: touch

default baz
default bar
```

当执行ninja命令时，会编译baz和bar，而不会编译foo。

> 示例见03_syntax_default_target



### (3) 使用Python代码生成build.ninja文件

在Nina的源码库中，`misc/ninja_syntax.py`提供Python模块，用于生成ninja文件，类似下面这样python代码

```python
ninja.rule(name='foo', command='bar', depfile='$out.d')
```



### (4) `.ninja_log`文件

每个`build.ninja`文件在执行ninja命令后，会生成一个log文件，名为`.ninja_log`文件，它位于root目录中。这个log文件会记录执行的command，当`build.ninja`文件的内容发生变化时，再次执行ninja命令，会重新编译。

说明

> 使用`builddir`变量可以指定`.ninja_log`文件所在的文件夹





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

[^11]:https://github.com/timniederhausen/gn-build/blob/master/config/BUILDCONFIG.gn#L6

