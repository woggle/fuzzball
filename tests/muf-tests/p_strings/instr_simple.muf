: main
    1
    "" "x" instr not and
    "foobarbazbar" "bar" instr 4 = and
    "barfoobar" "bar" instr 1 = and
    "barfoobazbar" "quux" instr not and
    "foo" "foo" instr 1 = and
    if me @ "Test passed." notify then
;
