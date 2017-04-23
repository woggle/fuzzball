: main
    me @ "Foo" newobject
    dup "_testprop" { #1234 #5678 #2356 }list array_put_reflist
    "_testprop" getprop "#1234 #5678 #2356" strcmp not
    if 
      me @ "Test passed." notify
    else
      me @ "Test failed." notify
    then
;
