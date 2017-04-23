: main
    1
    "" striptail "" strcmp not and
    "  foo  \r \r  " striptail "  foo" strcmp not and
    "bar        \r    " striptail "bar" strcmp not and
    "x" striptail "x" strcmp not and
    if me @ "Test passed." notify then
;
