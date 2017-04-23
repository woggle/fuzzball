: main
    1
    "" "x" rinstring not and
    "foobaRbazbAR" "bar" rinstring 10 = and
    "barfooBAr" "bAR" rinstring 7 = and
    "barfoobazbAr" "quux" rinstring not and
    "bar" "BAR" rinstring 1 = and
    "xxxbAr" "Bar" rinstring 4 = and
    if me @ "Test passed." notify then
;
