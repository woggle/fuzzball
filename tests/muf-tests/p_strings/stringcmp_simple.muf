: main
    1
    "abc" "AbC" stringcmp not and
    "abc" "abc " stringcmp 0 < and
    "abc " "abc" stringcmp 0 > and
    "cde" "abcde" stringcmp 0 > and
    "" "foo" stringcmp 0 < and
    "foo" "" stringcmp 0 > and
    "" "" stringcmp not and
    if me @ "Test passed." notify then
;
