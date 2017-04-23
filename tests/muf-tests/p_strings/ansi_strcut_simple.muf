: main
    1
    "" 0 ansi_strcut "" strcmp not swap "" strcmp not and and
    "foobar" 3 ansi_strcut "bar" strcmp not swap "foo" strcmp not and and
    "foobar" 6 ansi_strcut "" strcmp not swap "foobar" strcmp not and and
    "foobar" 7 ansi_strcut "" strcmp not swap "foobar" strcmp not and and
    "foobar" 0 ansi_strcut "foobar" strcmp not swap "" strcmp not and and
    "\[[0mfoo\[[3;03mbar\[[0m" 6 ansi_strcut
        "\[[0m" strcmp not
        swap "\[[0mfoo\[[3;03mbar" strcmp not and and
    "\[[0mfoo\[[3;03mbar\[[0m" 7 ansi_strcut
        "" strcmp not
        swap "\[[0mfoo\[[3;03mbar\[[0m" strcmp not and and
    "\[[0mfoo\[[3;03mbar\[[0m" 2 ansi_strcut
        "o\[[3;03mbar\[[0m" strcmp not
        swap "\[[0mfo" strcmp not and and
    "\[[0mfoo\[[3;03mbar\[[0m" 3 ansi_strcut
        "\[[3;03mbar\[[0m" strcmp not
        swap "\[[0mfoo" strcmp not and and
    "\[[0mfoo\[[3;03mbar\[[0m" 0 ansi_strcut
        "\[[0mfoo\[[3;03mbar\[[0m" strcmp not
        swap "" strcmp not  and and
    if me @ "Test passed." notify then
;
