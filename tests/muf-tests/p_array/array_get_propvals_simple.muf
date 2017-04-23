: main
    me @ "Foo" newobject
    dup "_test/_bar" 1 setprop
    dup "_test/quux" #2 setprop
    dup "_test/xyxxy" "stuff" setprop
    dup "_test/.secret" "#1&#0" parselock setprop
    dup "_test/.verysecret" 2.0 setprop
    dup "_test" array_get_propvals
    {
            "_bar" 1 
            "quux" #2
            "xyxxy" "stuff"
            ".secret" "#1&#0" parselock
            ".verysecret" 2.0
    }dict
    array_compare 0 = if
      me @ "Test passed." notify
    else
      me @ "Test failed." notify
    then
;
