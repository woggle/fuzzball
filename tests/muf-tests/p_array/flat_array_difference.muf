: main
    { 3 4 5 "test" "test2" #2 }list
    { #2 "other" "test2" }list
    { 1 2 3 "test" #1 }list
    3 array_ndiff
    0 array_sort
    { 1 2 #1 }list
    0 array_sort
    array_compare 0 = if
      me @ "Test passed." notify
    else
      me @ "Test failed." notify
    then
;
