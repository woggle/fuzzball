: main
    me @ "Foo" newobject
    dup "_testprop" "#1234 #5678 #2356" setprop
    dup "_testprop" array_get_reflist
    { #1234 #5678 #2356 }list array_compare 0 = 
    if 
      me @ "Test passed." notify
    else
      me @ "Test failed." notify
    then
;
