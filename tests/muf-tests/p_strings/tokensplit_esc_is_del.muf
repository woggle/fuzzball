: main
    1
    "foo//bar/baz/quux"   "/"   "/x"   TOKENSPLIT
    3 array_make
    "foo/bar"   "baz/quux"   "/"
    3 array_make
    array_compare 0 =
    if me @ "Test passed." notify then
;
