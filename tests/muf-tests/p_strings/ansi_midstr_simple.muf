: main
    1
    "" 1 0 ansi_midstr "" strcmp not and
    "foobar" 4 3 ansi_midstr "bar" strcmp not and
    "foobar" 4 4 ansi_midstr "bar" strcmp not and
    "foobar" 7 2 ansi_midstr "" strcmp not and
    "foobar" 8 2 ansi_midstr "" strcmp not and
    "foobar" 1 7 ansi_midstr "foobar" strcmp not and
    "foobar" 1 6 ansi_midstr "foobar" strcmp not and
    "foobar" 1 5 ansi_midstr "fooba" strcmp not and
    "\[[0mfoo\[[3;03mbar\[[0m" 1 6 ansi_midstr
        "\[[0mfoo\[[3;03mbar" strcmp not and
    "\[[0mfoo\[[3;03mbar\[[0m" 6 2 ansi_midstr
        "r\[[0m" strcmp not and
    "\[[0mfoo\[[3;03mbar\[[0m" 6 1 ansi_midstr
        "r" strcmp not and
    "\[[0mfoo\[[3;03mbar\[[0m" 7 1 ansi_midstr
        "\[[0m" strcmp not and
    "\[[0mfoo\[[3;03mbar\[[0m" 1 7 ansi_midstr
        "\[[0mfoo\[[3;03mbar\[[0m" strcmp not and
    "\[[0mfoo\[[3;03mbar\[[0m" 3 3 ansi_midstr
        "o\[[3;03mba" strcmp not and
    "\[[0mfoo\[[3;03mbar\[[0m" 4 4 ansi_midstr
        "\[[3;03mbar\[[0m" strcmp not and
    "\[[0mfoo\[[3;03mbar\[[0m" 4 0 ansi_midstr
        "" strcmp not and
    if me @ "Test passed." notify then
;
