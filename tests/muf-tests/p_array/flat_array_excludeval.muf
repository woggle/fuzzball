: main
    { #5 #10 #15 #10 #20 }list #10 array_excludeval
    { 0 2 4 }list array_compare 0 =
    if
      me @ "Test passed." notify
    else
      me @ "Test failed." notify
    then
;
