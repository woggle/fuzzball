: main
    #0 "TestRoom" newroom var! testRoom
    me @ testRoom @ moveto
    testRoom @ "TestObject" newobject var! roomObj
    testRoom @ "TestObject" newobject var! roomObj2
    0 var! count
    1
    begin
        "TestObject" match dup var! lastMatch roomObj2 @ = while
        count @ 1 + dup count ! 100000 < while
    repeat
    lastMatch @ roomObj @ = and
    begin
        "TestObject" match dup lastMatch ! roomObj @ = while
        count @ 1 + dup count ! 100000 < while
    repeat
    lastMatch @ roomObj2 @ = and
    if me @ "Test passed." notify then
;
