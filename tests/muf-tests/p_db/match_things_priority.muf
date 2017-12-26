: main
    #0 "TestRoom" newroom var! testRoom
    me @ testRoom @ moveto
    testRoom @ "TestObject" newobject var! roomObj
    1
    "TestObject" match roomObj @ = and
    me @ "TestObject" newobject var! meObj
    "TestObj" match #-2 = and
    meObj @ "TestObject Longer" setname
    "TestObject" match roomObj @ = and
    "TestObject L" match meObj @ = and
    meObj @ "TestObject" setname
    roomObj @ "TestObject Longer" setname
    "TestObject" match meObj @ = and
    "TestObj" match #-2 = and
    "TestObject L" match roomObj @ = and
    if me @ "Test passed." notify then
;
