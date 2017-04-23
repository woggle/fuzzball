: main
    { 1 2 3 "test" "test2" #1 #2 { 42 }list { 43 45 }list }list
    { 1 2 3 "test" "test2" #2 { 42 }list { 43 45 }list }list
    { 2 3 #2 "other" "test2" { 43 45 }list }list
    3 array_nintersect
    0 array_sort
    { 2 3 "test2" #2 { 43 45 }list }list
    0 array_sort
    array_compare 0 = if
      me @ "Test passed." notify
    else
      me @ "Test failed." notify
    then
;
