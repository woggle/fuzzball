: main
    me @ "Foo" newobject
    dup "_testdir"
    {
            1 
            #2
            "stuff"
            "#1&#0" parselock
            2.0
    }list
    array_put_proplist
    dup "_testdir#/1" getprop 1 = 
    over "_testdir#/2" getprop dup dbref? swap #2 = and and
    over "_testdir#/3" getprop "stuff" strcmp not and
    over "_testdir#/4" getprop unparselock "#1&#0" parselock unparselock strcmp not and
    over "_testdir#/5" getprop 2.0 = and
    over "_testdir#" getprop 5 = and
    if 
      me @ "Test passed." notify
    else
      me @ "Test failed." notify
    then
;
