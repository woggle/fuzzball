: main
    me @ "FooBar" newobject var! obj
    me @ "SomeVehicle" newobject var! vehicle
    vehicle @ "V" set
    1
    obj @ location me @ = and
    obj @ #0 moveto obj @ location #0 = and
    obj @ vehicle @ moveto obj @ location vehicle @ = and
    vehicle @ contents obj @ = and
    if me @ "Test passed." notify then
;
