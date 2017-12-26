: main
    me @ "FooBar" newobject var! obj
    1
    obj @ ok? and
    obj @ thing? and
    obj @ recycle
    obj @ ok? not and
    obj @ thing? not and
    if me @ "Test passed." notify then
;
