: main
    { #5 #10 #15 #10 #20 }list #10 array_findval  
    { 1 3 }list array_compare 0 =
    if
      me @ "Test passed." notify
    else
      me @ "Test failed." notify
    then
;
