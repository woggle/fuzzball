: main
    1
    prog compiled? and
    "tempprogram.muf" newprogram var! testprog
    testprog @ compiled? not and
    testprog @ {
        ": foo"
        "    42"
        ";"
        "PUBLIC foo"
        ": main 0 ;"
    }list dup var! progtext program_setlines
    testprog @ 0 0 program_getlines progtext @ array_compare 0 = and
    testprog @ compiled? not and
    testprog @ 0 compile 0 > and
    testprog @ compiled? and
    testprog @ uncompile
    testprog @ compiled? not and
    testprog @ "foo" call 42 = and
    testprog @ compiled? and
    if me @ "Test passed." notify then
;
(
BEFORE:@set test.muf=W
)
