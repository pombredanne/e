# -*- python -*-
{
  'target_defaults': {
    'type': 'executable',
    'cflags': ['-pedantic', '-Wall', '-std=c++11'],
    'conditions': [
       ['OS=="linux"', {
         'ldflags': [
           '-pthread',
          ],
          'libraries': [
            '-lboost_system',
            '-lboost_program_options',
            '<!@(pkg-config --libs-only-l libglog)',
            '<!@(pkg-config --libs-only-l icu-uc)',
            '<!@(pkg-config --libs-only-l ncursesw)',
            '-ltcmalloc',
            '-lunwind',
            '-lv8',
          ],
         'defines': [ 'USE_LINUX', ],
    }]],
    'sources': [
        'src/assert.cc',
        'src/buffer.cc',
        'src/bundled_core.cc',
        'src/curses_window.cc',
        'src/embeddable.cc',
        'src/flags.cc',
        'src/js.cc',
        'src/js_curses.cc',
        'src/js_curses_window.cc',
        'src/js_errno.cc',
        'src/js_signal.cc',
        'src/js_sys.cc',
        'src/keycode.cc',
        'src/line.cc',
        'src/list_environment.cc',
        'src/main.cc',
        'src/mmap.cc',
        'src/state.cc',
        'src/unicode.cc',
    ],
    'defines': [ 'USE_CURSES', 'TAB_SIZE=4', ],
  },
  'targets': [
    {
      'target_name': 'e',
      'cflags': ['-g'],
      'defines': [ 'DEBUG', ],
    },
  ],
}
