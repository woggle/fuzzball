: main
    1
    #0 "testExit" newexit var! theExit
    #0 "otherExit" newexit var! otherExit
    theExit @ getlink #-1 = and
    theExit @ getlinks 0 = and
    theExit @ getlinks_array array_count 0 = and
    theExit @ #0 setlink
    theExit @ getlink #0 = and
    theExit @ getlinks 1 = swap #0 = and and
    theExit @ getlinks_array { #0 }list array_compare 0 = and
    theExit @ { otherExit @ #0 }list setlinks_array
    theExit @ getlinks_array { otherExit @ #0 }list array_compare 0 = and
    theExit @ getlinks array_make { otherExit @ #0 }list array_compare 0 = and
    theExit @ getlink otherExit @ = and
    if me @ "Test passed." notify then
;
