: main
    me @ "FooBar" newobject var! obj
    obj @ "V" set
    me @ "SomeVehicle" newobject var! vehicle
    vehicle @ "V" set
    obj @ vehicle @ moveto
    0 try vehicle @ obj @ moveto catch
        "contain itself" instring if me @ "Test passed." notify then
    endcatch
;
