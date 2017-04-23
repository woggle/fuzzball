: main
    {
        {
            "a" 3.14
        }dict
    }list
    "%4.2[a]f"
    array_fmtstrings { "3.14" }list array_compare 0 = if
        me @ "Test passed." notify
    then
;
