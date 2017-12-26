: main
    me @ "FooBar" newobject var! obj
    {
        obj @ "exitOne" newexit
        obj @ "exitTwo" newexit
        obj @ "exitThree" newexit
    }list 0 array_sort var! contained
    1
    obj @ exits contained @ swap array_findval array_count 0 > and
    obj @ exits next contained @ swap array_findval array_count 0 > and
    obj @ exits next next contained @ swap array_findval array_count 0 > and
    obj @ exits next next next #-1 = and
    obj @ exits_array 0 array_sort contained @ array_compare 0 = and
    if me @ "Test passed." notify then
;
