: main
    { #5 #10 #15 #10 #20 }list 
    { #5 #10 #16 #10 #20 }list array_compare
    0 <
    { #5 #10 #15 #10 #21 }list 
    { #5 #10 #15 #10 #20 }list array_compare
    0 > and
    { #5 "#1&#2" parselock }list 
    { #5 "#1|#2" parselock }list array_compare
    0 != and
    if
      me @ "Test passed." notify
    else
      me @ "Test failed." notify
    then
;
