: main
    1
    "foo/bar"   "'"   "/"   TOKENSPLIT
    3 array_make
    "foobar"   ""   ""
    3 array_make
    array_compare 0 =
    if me @ "Test passed." notify then
;
