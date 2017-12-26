: main
    #0 "TestRoom" newroom var! testRoom
    1
    testRoom @ "TestRoom" rmatch #-1 = and
    testRoom @ "TestObject" newobject var! testObject
    testRoom @ "TestObject" rmatch testObject @ = and
    testObject @ me @ moveto
    testRoom @ "TestObject" rmatch #-1 = and
    testRoom @ "testExit;otherTestExit" newexit var! testExit
    testRoom @ "otherTestExit" rmatch testExit @ =  and
    testRoom @ "testExit" rmatch testExit @ = and
    testExit @ testObject @ moveto
    testObject @ testRoom @ moveto
    testRoom @ "testExit" rmatch #-1 = and
    testRoom @ "TestOther" newobject var! otherTestObject
    testRoom @ "TestO" rmatch #-2 = and
    if me @ "Test passed." notify then
;
