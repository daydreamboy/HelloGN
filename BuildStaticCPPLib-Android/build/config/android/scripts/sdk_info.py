#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""Collects information about the SDK and return them as JSON file."""

import argparse
import json
import os
import re
import subprocess
import sys
from distutils.version import LooseVersion

# Patterns used to extract the Xcode version and build version.
XCODE_VERSION_PATTERN = re.compile(r'Xcode (\d+)\.(\d+)')
XCODE_BUILD_PATTERN = re.compile(r'Build version (.*)')


def GetCommandOutput(command):
  """Returns the output of `command` as a string."""
  return subprocess.check_output(command, encoding='utf-8')


# Note: Android ABI, see https://developer.android.com/ndk/guides/abis
def GetAndroidABIName(target_cpu):
  """Returns the name of the |target_cpu| using Apple's convention."""
  return {
      'x86_64': 'x86_64',
      'arm64-v8a': 'aarch64',
      'x86': 'i686',
      'armeabi-v7a': 'armv7',
  }.get(target_cpu, target_cpu)


def GetPlatform(target_environment):
  """Returns the platform for |target_environment|."""
  return {
      'simulator': 'android',
      'device': 'android'
  }[target_environment]


def GetPlaformDisplayName(target_environment):
  """Returns the platform display name for |target_environment|."""
  return {
      'simulator': 'AndroidSimulator',
      'device': 'AndroidOS'
  }[target_environment]


def ExtractOSVersion():
  """Extract the version of macOS of the current machine."""
  return GetCommandOutput(['sw_vers', '-buildVersion']).strip()


def ExtractXcodeInfo():
  """Extract Xcode version and build version."""
  version, build = None, None
  for line in GetCommandOutput(['xcodebuild', '-version']).splitlines():
    match = XCODE_VERSION_PATTERN.search(line)
    if match:
      major, minor = match.group(1), match.group(2)
      version = major.rjust(2, '0') + minor.ljust(2, '0')
      continue

    match = XCODE_BUILD_PATTERN.search(line)
    if match:
      build = match.group(1)
      continue

  assert version is not None and build is not None
  return version, build


def ExtractNDKInfo(info):
  """Extract information about the SDK."""
  # Step1: check ANDROID_NDK_HOME first
  ndk_path = os.environ.get('ANDROID_NDK_HOME')
  if ndk_path:
    return ndk_path

  # Step2: check AndroidStudio ndk
  android_studo_ndk = os.path.join(os.path.expanduser("~"), "Library/Android/sdk/ndk/")
  if not os.path.isdir(android_studo_ndk):
      return ""
  
  contents = os.listdir(android_studo_ndk)
  # Get a list of all subdirectories in the folder
  subdirs = [d for d in contents if os.path.isdir(os.path.join(android_studo_ndk, d))]

  # Find the directory with the largest version number
  max_version_dir = ""
  max_version = LooseVersion("0.0.0")
  for subdir in subdirs:
      try:
          version = LooseVersion(subdir)
          if version > max_version:
              max_version = version
              max_version_dir = subdir
      except ValueError:
          pass

  # Print the name of the directory with the largest version number
  if not max_version_dir:
      return ""

  if info == "version":
      return max_version_dir

  if info == "path":
    ndk_path = os.path.join(android_studo_ndk, max_version_dir)
    return ndk_path

  if info == "toolchain":
    toolchain_path = os.path.join(android_studo_ndk, max_version_dir, "toolchains")
    if os.path.isdir(toolchain_path):
      return toolchain_path
    
  if info == "clang_path":
    clang_path = os.path.join(android_studo_ndk, max_version_dir, "toolchains/llvm/prebuilt/darwin-x86_64/bin/clang")
    if os.path.isfile(clang_path):
      return clang_path
    
  if info == "clangcpp_path":
    clangcpp_path = os.path.join(android_studo_ndk, max_version_dir, "toolchains/llvm/prebuilt/darwin-x86_64/bin/clang++")
    if os.path.isfile(clangcpp_path):
      return clangcpp_path

  return ""


def GetDeveloperDir():
  """Returns the developer dir."""
  return GetCommandOutput(['xcode-select', '-print-path']).strip()


# Note: The triple has the general format <arch><sub>-<vendor>-<sys>-<abi>, where:
# arch = x86, arm, thumb, mips, etc.
# sub = for ex. on ARM: v5, v6m, v7a, v7m, etc.
# vendor = pc, apple, nvidia, ibm, etc.
# sys = none, linux, win32, darwin, cuda, etc.
# abi = eabi, gnu, android, macho, elf, etc.
# @see https://stackoverflow.com/a/40890321
# 
# Solution: use cmake to compile, and check its ninja file to find the correct target triple name
def GetTargetTripe(target_cpu, deployment_target):
  """Returns the target triple name"""
  if target_cpu == "armv7":
    return target_cpu + '-none-linux-androideabi' + deployment_target
  else:
    return target_cpu + '-none-linux-android' + deployment_target


def GetSDKInfoForCpu(target_cpu, environment, sdk_version, deployment_target):
  """Returns a dictionary with information about the SDK."""
  platform = GetPlatform(environment)
  sdk_version = sdk_version or ExtractNDKInfo('version')

  deployment_target = deployment_target or sdk_version

  target = GetTargetTripe(target_cpu, deployment_target)

  sdk_info = {}
  # sdk_info['compiler'] = 'com.apple.compilers.llvm.clang.1_0'
  sdk_info['is_simulator'] = environment == 'simulator'
  sdk_info['macos_build'] = ExtractOSVersion()
  sdk_info['platform'] = platform
  sdk_info['platform_name'] = GetPlaformDisplayName(environment)
  sdk_info['ndk_path'] = ExtractNDKInfo('path')
  sdk_info['toolchain_path'] = ExtractNDKInfo('toolchain')
  sdk_info['ndk_version'] = sdk_version
  sdk_info['target'] = target
  sdk_info['clang_path'] = ExtractNDKInfo('clang_path')
  sdk_info['clangcpp_path'] = ExtractNDKInfo('clangcpp_path')

  return sdk_info


def ParseArgs(argv):
  """Parses command line arguments."""
  parser = argparse.ArgumentParser(
      description=__doc__,
      formatter_class=argparse.ArgumentDefaultsHelpFormatter)

  parser.add_argument(
      '-t', '--target-cpu', default='x86_64',
      choices=('x86', 'x86_64', 'armeabi-v7a', 'arm64-v8a'),
      help='target cpu')
  parser.add_argument(
      '-e',
      '--target-environment',
      default='simulator',
      choices=('simulator', 'device'),
      help='target environment')
  parser.add_argument(
      '-s', '--sdk-version',
      help='version of the sdk')
  parser.add_argument(
      '-d', '--min-sdk-version',
      help='Android deployment target min version')
  parser.add_argument(
      '-o', '--output', default='-',
      help='path of the output file to create; - means stdout')

  return parser.parse_args(argv)


def main(argv):
  args = ParseArgs(argv)

  sdk_info = GetSDKInfoForCpu(GetAndroidABIName(args.target_cpu), args.target_environment, args.sdk_version, args.min_sdk_version)

  if args.output == '-':
    sys.stdout.write(json.dumps(sdk_info))
  else:
    with open(args.output, 'w') as output:
      output.write(json.dumps(sdk_info))


if __name__ == '__main__':
  sys.exit(main(sys.argv[1:]))
