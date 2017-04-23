: main
    1
    "abc" "AbC" 3 strncmp 0 > and
    "abc" "AbC" 4 strncmp 0 > and
    "abc" "AbC" 2 strncmp 0 > and
    "abc" "abc " 4 strncmp 0 < and
    "abc" "abc " 5 strncmp 0 < and
    "abc" "abc " 3 strncmp 0 = and
    "abc " "abc" 4 strncmp 0 > and
    "abc " "abc" 3 strncmp 0 = and
    "abc " "abc" 2 strncmp 0 = and
    "cde" "abcde" 1 strncmp 0 > and
    "cde" "abcde" 10 strncmp 0 > and
    "cde" "abcde" 0 strncmp 0 = and
    "" "foo" 1 strncmp 0 < and
    "foo" "" 1 strncmp 0 > and
    "" "" 1 strncmp not and
    if me @ "Test passed." notify then
;
