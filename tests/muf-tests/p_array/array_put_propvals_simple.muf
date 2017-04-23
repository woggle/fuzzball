: main
    me @ "Foo" newobject
    dup "_testdir"
    {
            "first" 1 
            "second" #2
            "third" "stuff"
            "fourth" "#1&#0" parselock
            "fifth" 2.0
    }dict
    array_put_propvals
    dup "_testdir/first" getprop 1 = 
    over "_testdir/second" getprop dup dbref? swap #2 = and and
    over "_testdir/third" getprop "stuff" strcmp not and
    over "_testdir/fourth" getprop unparselock "#1&#0" parselock unparselock strcmp not and
    over "_testdir/fifth" getprop 2.0 = and
    if 
      me @ "Test passed." notify
    else
      me @ "Test failed." notify
    then
;
