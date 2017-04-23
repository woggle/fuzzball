: main
    1
    "" ansi_strlen 0 = and
    "foobar" ansi_strlen 6 = and
    "\[[0mfoo\[[3;03mbar\[[0m" ansi_strlen 6 = and
    if me @ "Test passed." notify then
;
