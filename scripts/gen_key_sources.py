#!/usr/bin/env python

import datetime
import optparse
import re
import sys

h_template = """
// -*- C++ -*-
// Copyright %(current_year)d, Evan Klitzke <evan@eklitzke.org>
//
// This file is AUTOGENERATED by gen_key_sources.py, do not edit by hand!

#ifndef KEYCODE_H_
#define KEYCODE_H_

#include <string>

namespace e {
  class KeyCode {
    private:
      int code_;
      std::string short_name_;
    public:
      explicit KeyCode(int code,
                       const std::string &short_name);
      explicit KeyCode(int code);
      const std::string& get_name(void) const;
      bool is_ascii(void) const;
      int get_code(void) const;
      char get_char(void) const;
  };

  namespace keycode {
    const KeyCode& curses_code_to_keycode(int);
  }
}

#endif  // KEYCODE_H_
"""

cc_template = """
// -*- C++ -*-
// Copyright %(current_year)d, Evan Klitzke <evan@eklitzke.org>
//
// This file is AUTOGENERATED by gen_key_sources.py, do not edit by hand!

#include <string>

#include "./%(h_name)s"

namespace e {
  KeyCode::KeyCode(int code, const std::string &short_name)
    :code_(code), short_name_(short_name) {
  }

  KeyCode::KeyCode(int code)
    :code_(code) {
    if (code <= 127) {
      const char name[2] = { static_cast<char>(code), 0 };
      short_name_ = name;
    }
  }

  const std::string&
  KeyCode::get_name(void) const {
    return short_name_;
  }

  bool
  KeyCode::is_ascii(void) const {
    return code_ <= 0xff;
  }

  int
  KeyCode::get_code(void) const {
    return code_;
  }

  // XXX: it's unspecified whether this is a signed or unsigned char!
  char
  KeyCode::get_char(void) const {
    if (code_ > 0xff) {
      return static_cast<char>(code_ & 0xff);
    } else {
      return static_cast<char>(code_);
    }
  }

  namespace keycode {
    const size_t max_code = %(max_code)d;
    KeyCode keycode_arr[max_code + 1] = {
%(codes)s
    };

    const KeyCode&
    curses_code_to_keycode(int code) {
      return keycode_arr[static_cast<size_t>(code)];
    }
  }
}
"""

key_regex = re.compile(r'^([_a-z0-9]+)\s+[a-zA-Z0-9]+\s+str\s+[a-zA-Z0-9;@%&*#!]+\s+([_A-Z()0-9]+)\s+([-0-9]+)\s+[-A-Z*]+\s+(.*)$')
octal_regex = re.compile(r'^0[0-9]+$')

if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option('-o', '--output-prefix', default='keycode', help='output prefix')
    opts, args = parser.parse_args()
    if len(args) != 1:
        parser.error('must give exactly one argument')
        sys.exit(1)
    try:
        in_file = open(args[0], 'r')
    except IOError:
        parser.error('failed to open capabilities file %r' % (args[1],))

    values = []
    try:
        for line in in_file:
            if not line.startswith('key_'):
                continue
            m = key_regex.match(line)
            if not m:
                print >> sys.stderr, 'failed to parse line %r' % (line,)
                sys.exit(1)
            name, macro, code, description = m.groups()
            if code == '-':
                code = 0
            elif octal_regex.match(code):
                code = int(code, 8)
            else:
                print >> sys.stderr, 'failed to parse octal code %r' % (code,)
            values.append((name, macro, code, description))
    finally:
        in_file.close()

    # OK, we were able to parse the file; generate the C++ files

    def comparator(a, b):
        ak = a[2]
        bk = b[2]
        if ak == 0 and bk == 0:
            return cmp(a[0], b[0])
        elif ak == 0:
            return 1
        elif bk == 0:
            return -1
        else:
            return cmp(a[2], b[2])

    values.sort(comparator)
    value_map = dict((code, (name, description)) for name, _, code, description in values)
    max_code = max(value_map.iterkeys())

    current_year = datetime.date.today().year
    h_name = opts.output_prefix + '.h'
    cc_name = opts.output_prefix + '.cc'

    code_arr = []
    for code in xrange(max_code + 1):
        if code and code in value_map:
            name, description = value_map[code]
            code_arr.append('      KeyCode(%d, "%s"),  // %s' % (code, name, description))
        else:
            code_arr.append('      KeyCode(%d),' % (code,))

    with open(h_name, 'w') as h_file:
        h_file.write(h_template.lstrip() % {'current_year': current_year})

    with open(cc_name, 'w') as cc_file:
        cc_file.write(cc_template.lstrip() % ({'current_year': current_year,
                                               'codes': '\n'.join(code_arr),
                                               'h_name': h_name,
                                               'max_code': max_code}))
