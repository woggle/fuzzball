: main
    1
    "abc" "AbC" strcmp 0 > and
    "abc" "abc " strcmp 0 < and
    "abc " "abc" strcmp 0 > and
    "cde" "abcde" strcmp 0 > and
    "" "foo" strcmp 0 < and
    "foo" "" strcmp 0 > and
    "" "" strcmp not and
    if me @ "Test passed." notify then
;
