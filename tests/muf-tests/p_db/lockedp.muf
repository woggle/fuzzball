: main
    me @ "FooBar" newobject var! obj
    obj @ "_/lok" "_testprop:testval" parselock setprop
    1
    me @ obj @ locked? and
    me @ "_testprop" "testval" setprop me @ obj @ locked? not and
    if me @ "Test passed." notify then
;
