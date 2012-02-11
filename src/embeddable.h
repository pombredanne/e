// -*- C++ -*-
// Copyright 2012, Evan Klitzke <evan@eklitzke.org>

#ifndef EMBEDDABLE_H_
#define EMBEDDABLE_H_

#include <v8.h>
#include <map>
#include <string>
#include <vector>

namespace e {

using v8::Context;
using v8::FunctionTemplate;
using v8::InvocationCallback;
using v8::Handle;
using v8::Persistent;
using v8::Value;

class Embeddable {
 protected:
  Persistent<Context> context_;
 public:
  virtual ~Embeddable() { context_.Dispose(); }
  Handle<FunctionTemplate> ToCallable(InvocationCallback func);
  Handle<Value> ToExternal();
  template <typename T> static T *FromExternal(Handle<Value>);
};
}

#endif  // EMBEDDABLE_H_