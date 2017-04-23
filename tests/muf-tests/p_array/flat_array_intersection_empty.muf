: main
    { 1 2 3 "test" #1 }list
    { 3 4 5 "test" "test2" #2 }list
    { "other" }list
    3 array_nintersect
    array_count 0 = if
      me @ "Test passed." notify
    else
      me @ "Test failed." notify
    then
;
