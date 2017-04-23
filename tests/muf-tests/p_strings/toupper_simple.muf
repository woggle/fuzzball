: main
    1
    "" toupper "" strcmp not and
    "foo" toupper "FOO" strcmp not and
    "fOo123bar" toupper "FOO123BAR" strcmp not and
    if me @ "Test passed." notify then
;
