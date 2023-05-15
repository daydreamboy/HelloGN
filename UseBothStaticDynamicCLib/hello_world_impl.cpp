#include "HelloWorld.hpp"

using namespace HelloDjinni;

class HelloWorldImpl : public HelloWorld {
public:
    static std::shared_ptr<HelloWorld> create() {
        return std::make_shared<HelloWorldImpl>();
    }
    std::string fromCpp() {
        return "Hello From C++!";
    }
};
