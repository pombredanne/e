// Copyright 2012, Evan Klitzke <evan@eklitzke.org>

#include <cassert>
#include <string>
#include <v8.h>

#include "./log.h"
#include "./state.h"

using namespace v8;

namespace e {

  namespace js {
    static Handle<Value> LogCallback(const Arguments& args) {
      if (args.Length() < 1) {
        return Undefined();
      }
      HandleScope scope;
      Handle<Value> arg = args[0];
      String::Utf8Value value(arg);
      e::log::log_string(*value);
      return Undefined();
    }

    //static Handle<Value> KeyPressCallback(const Arguments &args) {
    //}
  }

  State::State(const std::string &script)
    :active_buffer_(new Buffer("*temp*")) {

    HandleScope handle_scope;

    Handle<ObjectTemplate> global = ObjectTemplate::New();
    global->Set(String::New("log"), FunctionTemplate::New(js::LogCallback));

    // set up the global script context
    context_ = Context::New(NULL, global);

    Context::Scope context_scope(context_);

    // compile the JS source code, and run it once
    Handle<String> source = String::New(script.c_str(), script.size());
    Handle<Script> scr = Script::Compile(source);
    scr->Run();

    // get the onKeyPress function
    Handle<String> keypress_cb_name = String::New("onKeyPress");
    Handle<Value> onkeypress_val = context_->Global()->Get(keypress_cb_name);
    if (!onkeypress_val->IsFunction()) {
      assert(false);
    }

    // cast it to a function
    Handle<Function> onkeypress_fun = Handle<Function>::Cast(onkeypress_val);

    // that to remain after this call returns
    onkeypress_ = Persistent<Function>::New(onkeypress_fun);

  }

  State::~State() {
    context_.Dispose();
  }


  Buffer *
  State::get_active_buffer(void) {
    return active_buffer_;
  }

  std::vector<Buffer *> *
  State::get_buffers(void) {
    return &buffers_;
  }

  bool
  State::handle_key(const KeyCode &k) {
    if (k.is_ascii() && k.get_char() == 'q') {
      return false;
    }

    HandleScope scope;

    const int argc = 1;
    Handle<Value> argv[argc] = { Integer::New(k.get_code()) };
    Handle<Value> result = onkeypress_->Call(context_->Global(), argc, argv);

    return true;
  }
}
