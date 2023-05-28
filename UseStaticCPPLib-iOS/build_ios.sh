gn gen ios_out/arm64 --args='is_debug=true target_os="ios" target_cpu="arm64" ios_enable_code_signing=false'
ninja -C ios_out/arm64
