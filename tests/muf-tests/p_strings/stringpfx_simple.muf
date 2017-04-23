: main
    1
    "" "" stringpfx and
    "foo" "foo" stringpfx and
    "foobar" "foo" stringpfx and
    "foobar" "FOO" stringpfx and
    "" "foo" stringpfx not and
    "foo" "foobar" stringpfx not and
    "foo" "fou" stringpfx not and
    "foobar" "fou" stringpfx not and
    if me @ "Test passed." notify then
;
