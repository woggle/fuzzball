: main
    { #5 #10 #15 #10 #20 }list 
    { 0 3 4 }list array_extract
    { 0 #5  3 #10  4 #20 }dict array_compare 0 =
    if
      me @ "Test passed." notify
    else
      me @ "Test failed." notify
    then
;
