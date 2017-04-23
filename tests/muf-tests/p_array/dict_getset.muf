: main
    { 
        "first" 1.0
        "second" "value-second"
    }dict
    dup "first" [] 1.0 =
    over "second" [] "value-second" strcmp not and
    if me @ "Test passed." notify then
;
