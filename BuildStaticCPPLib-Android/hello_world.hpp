#pragma once

#include <memory>
#include <string>

namespace HelloDjinni {

class HelloWorld {
public:
    virtual ~HelloWorld() {}

    static std::shared_ptr<HelloWorld> create();

    virtual std::string fromCpp() = 0;
};

}  // namespace HelloDjinni
