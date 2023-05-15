// Copyright 2014 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

#include <stdio.h>
#include <iostream>

#include "hello_shared.h"
#include "hello_static.h"
#include "HelloWorld.hpp"

using namespace HelloDjinni;
using namespace std;

int main(int argc, char* argv[]) {
  printf("%s, %s\n", GetStaticText(), GetSharedText());

  std::shared_ptr<HelloWorld> hello = HelloWorld::create();
  std::cout << hello->fromCpp() << std::endl;

  return 0;
}
