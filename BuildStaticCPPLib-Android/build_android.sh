set -x
set -e

libName="libhello_android_static_cpp.a"

if [[ $1 = "device" ]]; then
  gn gen android_out/arm64 --args='target_os="android" target_cpu="arm64" target_environment="device"'
  ninja -C android_out/arm64
elif [[ $1 = "simulator" ]]; then
  gn gen android_out/x64 --args='target_os="android" target_cpu="x64" target_environment="simulator"'
  ninja -C android_out/x64
elif [[ $1 = "all" ]]; then
  gn gen android_out/arm64 --args='target_os="android" target_cpu="arm64" target_environment="device"'
  ninja -C android_out/arm64

  gn gen android_out/x64 --args='target_os="android" target_cpu="x64" target_environment="simulator"'
  ninja -C android_out/x64

  mkdir -p ./android_out/all/obj
  lipo -create ./android_out/arm64/obj/${libName} ./android_out/x64/obj/${libName} -o ./android_out/all/obj/${libName}
  echo "create static library ($1) successfully!"
else
  echo "Must support a parameter"
fi