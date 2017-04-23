: main
    me @ "Foo" newobject
    dup "_test/_bar/_foo" 1 setprop
    dup "_test/quux" 2 setprop
    dup "_test/.secret/_stuff" 2 setprop
    dup "_test" array_get_propdirs
    0 array_sort
    { "_bar" ".secret" }list
    0 array_sort
    array_compare 0 = if
      me @ "Test passed." notify
    else
      me @ "Test failed." notify
    then
;
