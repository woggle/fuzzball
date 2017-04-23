: main
    { 1 2 3 "test" #1 }list
    { 3 4 5 "test" "test2" #2 }list
    { "other" }list
    3 array_nunion
    0 array_sort
    { 1 2 3 4 5 "test" "test2" "other" #1 #2 }list
    0 array_sort
    array_compare 0 = if
      me @ "Test passed." notify
    else
      me @ "Test failed." notify
    then
;
