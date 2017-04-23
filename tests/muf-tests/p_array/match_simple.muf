: main
    { 
        "first" "value-1-foobar"
        "second" "value-2-bar"
    }dict
    var! theArray

    1
    theArray @ "*s*" array_matchkey theArray @ array_compare 0 = and
    theArray @ "*fir*" array_matchkey { "first" "value-1-foobar" }dict array_compare 0 = and
    theArray @ "*none*" array_matchkey { }dict array_compare 0 = and
    theArray @ "*bar*" array_matchval theArray @ array_compare 0 = and
    theArray @ "*foo*" array_matchval { "first" "value-1-foobar" }dict array_compare 0 = and

    if me @ "Test passed." notify then
;
