: main
    1
    "ab//cd/'efg'hi//jk'lm"   "'"   "/"   TOKENSPLIT
    3 array_make
    "ab/cd'efg"   "hi//jk'lm"   "'"
    3 array_make
    array_compare 0 =
    if me @ "Test passed." notify then
;
