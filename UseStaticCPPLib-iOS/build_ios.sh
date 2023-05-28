
if [[ $1 = "device" ]]; then
  gn gen ios_out/arm64 --args='is_debug=true target_os="ios" target_cpu="arm64" ios_enable_code_signing=false'
  ninja -C ios_out/arm64
elif [[ $1 = "simulator" ]]; then
  gn gen ios_out/x64 --args='is_debug=true target_os="ios" target_cpu="x64" ios_enable_code_signing=false'
  ninja -C ios_out/x64
elif [[ $1 = "all" ]]; then
  gn gen ios_out/arm64 --args='is_debug=true target_os="ios" target_cpu="arm64" ios_enable_code_signing=false'
  ninja -C ios_out/arm64

  gn gen ios_out/x64 --args='is_debug=true target_os="ios" target_cpu="x64" ios_enable_code_signing=false'
  ninja -C ios_out/x64

  mkdir -p ./ios_out/all/obj
  lipo -create ./ios_out/arm64/obj/libhello_ios_static_cpp.a ./ios_out/x64/obj/libhello_ios_static_cpp.a -o ./ios_out/all/obj/libhello_ios_static_cpp.a
else
  echo "Must support a parameter"
fi