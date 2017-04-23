: main
    1
    "" "x" rinstr not and
    "foobarbazbar" "bar" rinstr 10 = and
    "barfoobar" "bar" rinstr 7 = and
    "barfoobazbar" "quux" rinstr not and
    "bar" "bar" rinstr 1 = and
    "xxxbar" "bar" rinstr 4 = and
    if me @ "Test passed." notify then
;
