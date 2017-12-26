: main
    #0 "TestRoom" newroom var! testRoom
    me @ testRoom @ moveto
    #0 "alpha;bravo;charlie" newexit var! zeroExit
    1
    "alpha" match zeroExit @ = and
    "bravo" match zeroExit @ = and
    "charlie" match zeroExit @ = and
    "delta" match #-1 = and
    testRoom @ "bravo;charlie;delta;echo" newexit var! roomExit
    "alpha" match zeroExit @ = and
    "bravo" match roomExit @ = and
    "charlie" match roomExit @ = and
    "delta" match roomExit @ = and
    "echo" match roomExit @ = and
    me @ "alpha;charlie;echo;foxtrot;golf" newexit var! meExit
    "alpha" match meExit @ = and
    "bravo" match roomExit @ = and
    "charlie" match roomExit @ = and
    "delta" match roomExit @ = and
    "echo" match roomExit @ = and
    "foxtrot" match meExit @ = and
    "golf" match meExit @ = and
    testRoom @ "SomeObject" newobject var! testObj
    testObj @ "alpha;bravo;echo;foxtrot" newexit var! testObjExit
    "alpha" match testObjExit @ = and
    "bravo" match roomExit @ = and
    "charlie" match roomExit @ = and
    "delta" match roomExit @ = and
    "echo" match roomExit @ = and
    "foxtrot" match testObjExit @ = and
    "golf" match meExit @ = and
    me @ "SomeObjectTwo" newobject var! testInvObj
    testInvObj @ "alpha;bravo;echo;foxtrot;golf" newexit var! testInvObjExit
    "alpha" match testInvObjExit @ = and
    "bravo" match roomExit @ = and
    "charlie" match roomExit @ = and
    "delta" match roomExit @ = and
    "echo" match roomExit @ = and
    "foxtrot" match testInvObjExit @ = and
    "golf" match testInvObjExit @ = and
    if me @ "Test passed." notify then
;
