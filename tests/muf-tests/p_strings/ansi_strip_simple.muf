: main
    1
    "" ansi_strip "" strcmp not and
    "foobar" ansi_strip "foobar" strcmp not and
    "\[[0mfoo\[[3;03mbar\[[0m" ansi_strip "foobar" strcmp not and
    "\[[00000foobarquux" ansi_strip "foobarquux" strcmp not and
    "stuff\[[35;45mstuff" ansi_strip "stuffstuff" strcmp not and
    if me @ "Test passed." notify then
;
