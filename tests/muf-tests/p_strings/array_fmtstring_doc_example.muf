: main
    {
        {
            "username" "Johnny"
            "count" 4
            "object" #18
            4  pi
        }dict
        {
            "username" "Ghaladahsk_Fadja"
            "count" 123
            "object" #97
            4 0.0
        }dict
    }list
    "%-16.15[username]s %3[count]i %5[object]d %4.2[4]f"
    array_fmtstrings
    dup 0 array_getitem me @ swap notify
    {
    "Johnny             4   #18 3.14"
    "Ghaladahsk_Fadj  123   #97 0.00"
    }list array_compare 0 =
    if me @ "Test passed." notify then
;
