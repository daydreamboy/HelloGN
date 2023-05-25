#include "hello_world.hpp"

using namespace HelloDjinni;

// Wanring: inline function maybe compiled into an empty static library
/*
class HelloWorldImpl : public HelloWorld {
public:
    std::shared_ptr<HelloWorld> create() {
        return std::make_shared<HelloWorldImpl>();
    }

    std::string fromCpp() {
        return "Hello From C++!";
    }
};
*/

class HelloWorldImpl : public HelloWorld {
public:
    // Note: should re-declare again for static member function
    static std::shared_ptr<HelloWorld> create();
    // Note: should re-declare again for pure virtual function
    std::string fromCpp() /*override*/;
};

// Override the static function in super class
// Use HelloWorld:: instead of HelloWorldImpl::, @see https://stackoverflow.com/questions/2642321/static-function-in-an-abstract-class
std::shared_ptr<HelloWorld> HelloWorld::create() {
    return std::make_shared<HelloWorldImpl>();
}

// Override the pure virtual function in super class
std::string HelloWorldImpl::fromCpp() {
    return "Hello From C++!";
}

