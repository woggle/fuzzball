: main
    1
    "" "x" instring not and
    "fOobArbazbar" "bar" instring 4 = and
    "baRfooBAr" "BAR" instring 1 = and
    "barFoobazbar" "quux" instring not and
    "FoO" "fOo" instring 1 = and
    if me @ "Test passed." notify then
;
