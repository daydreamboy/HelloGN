set -x
set -e

libName="libhello_ios_static_cpp.a"

if [[ $1 = "device" ]]; then
  gn gen ios_out/arm64 --args='target_os="ios" target_cpu="arm64"'
  ninja -C ios_out/arm64
elif [[ $1 = "simulator" ]]; then
  gn gen ios_out/x64 --args='target_os="ios" target_cpu="x64"'
  ninja -C ios_out/x64
elif [[ $1 = "all" ]]; then
  gn gen ios_out/arm64 --args='target_os="ios" target_cpu="arm64"'
  ninja -C ios_out/arm64

  gn gen ios_out/x64 --args='target_os="ios" target_cpu="x64"'
  ninja -C ios_out/x64

  mkdir -p ./ios_out/all/obj
  lipo -create ./ios_out/arm64/obj/${libName} ./ios_out/x64/obj/${libName} -o ./ios_out/all/obj/${libName}
  echo "create static library ($1) successfully!"
else
  echo "Must support a parameter"
fi