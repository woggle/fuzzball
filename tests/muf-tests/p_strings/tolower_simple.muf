: main
    1
    "" tolower "" strcmp not and
    "FOO" tolower "foo" strcmp not and
    "FOo123BaR" tolower "foo123bar" strcmp not and
    if me @ "Test passed." notify then
;
