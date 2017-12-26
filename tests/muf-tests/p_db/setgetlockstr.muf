: main
    me @ "FooBar" newobject var! obj
    obj @ "_testprop:testval" setlockstr
    1
    obj @ "_/lok" getprop unparselock "_testprop:testval" parselock unparselock strcmp not and
    obj @ getlockstr "_testprop:testval" parselock unparselock strcmp not and
    if me @ "Test passed." notify then
;
