: main
    me @ "Foo" newobject
    dup "_test#/1" 1 setprop
    dup "_test#/2" #2 setprop
    dup "_test#/3" "stuff" setprop
    dup "_test#/4" "#1&#0" parselock setprop
    dup "_test#/5" 2.0 setprop
    dup "_test#" 5 setprop
    dup "_test" array_get_proplist
    {
            1
            #2
            "stuff"
            "#1&#0" parselock
            2.0
    }list
    array_compare 0 = if
      me @ "Test passed." notify
    else
      me @ "Test failed." notify
    then
;
