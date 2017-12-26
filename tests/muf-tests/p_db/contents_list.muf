: main
    me @ "FooBar" newobject var! obj
    {
        me @ "ThingOne" newobject dup obj @ moveto
        me @ "ThingTwo" newobject dup obj @ moveto
        me @ "ThingThree" newobject dup obj @ moveto
    }list 0 array_sort var! contained
    1
    obj @ contents contained @ swap array_findval array_count 0 > and
    obj @ contents next contained @ swap array_findval array_count 0 > and
    obj @ contents next next contained @ swap array_findval array_count 0 > and
    obj @ contents next next next #-1 = and
    obj @ contents_array 0 array_sort contained @ array_compare 0 = and
    if me @ "Test passed." notify then
;
