set -x
set -e

TARGET_OS="android"
OUT_HOME="android_out"

# Note: target_cpu = ${ABI}, Android ABI, see https://developer.android.com/ndk/guides/abis
if [[ $1 = "device" ]]; then
  ARCH="arm64-v8a"

  gn gen ${OUT_HOME}/${ARCH} --args="target_os=\"${TARGET_OS}\" target_cpu=\"${ARCH}\" target_environment=\"device\""
  ninja -C ${OUT_HOME}/${ARCH}
elif [[ $1 = "simulator" ]]; then
  ARCH="x86_64"

  gn gen ${OUT_HOME}/${ARCH} --args="target_os=\"${TARGET_OS}\" target_cpu=\"${ARCH}\" target_environment=\"device\""
  ninja -C ${OUT_HOME}/${ARCH}
elif [[ $1 = "all" ]]; then
  # Step1 
  ARCH="arm64-v8a"

  gn gen ${OUT_HOME}/${ARCH} --args="target_os=\"${TARGET_OS}\" target_cpu=\"${ARCH}\" target_environment=\"device\""
  ninja -C ${OUT_HOME}/${ARCH}

  # Step2
  ARCH="x86_64"

  gn gen ${OUT_HOME}/${ARCH} --args="target_os=\"${TARGET_OS}\" target_cpu=\"${ARCH}\" target_environment=\"device\""
  ninja -C ${OUT_HOME}/${ARCH}
elif [[ $1 = "clean" ]]; then
  if [[ -x "$(command -v trash)" ]]; then
    trash ./android_out
  else
    rm -rf ./android_out
  fi
elif [[ $1 = "armeabi-v7a" ]]; then
  ARCH="armeabi-v7a"

  gn gen ${OUT_HOME}/${ARCH} --args="target_os=\"${TARGET_OS}\" target_cpu=\"${ARCH}\" target_environment=\"device\""
  ninja -C ${OUT_HOME}/${ARCH}
elif [[ $1 = "x86" ]]; then
  ARCH="x86"

  gn gen ${OUT_HOME}/${ARCH} --args="target_os=\"${TARGET_OS}\" target_cpu=\"${ARCH}\" target_environment=\"device\""
  ninja -C ${OUT_HOME}/${ARCH}
else
  echo "Must support a parameter"
fi