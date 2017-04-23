: main
    { 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 }list
    dup
    4 array_sort
    0 array_sort
    array_compare 0 = 
    if
      me @ "Test passed." notify
    else
      me @ "Test failed." notify
    then
;
