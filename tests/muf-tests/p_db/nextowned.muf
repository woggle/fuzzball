: main
    1
    #0 "TestObjectOne" newobject var! testObjectOne
    "TestPlayer" "dumbpassword" newplayer var! testPlayer
    testPlayer @ nextowned #-1 = and
    testObjectOne @ testPlayer @ setown
    testPlayer @ nextowned testObjectOne @ = and
    testObjectOne @ nextowned #-1 = and
    #0 "TestObjectTwo" newobject var! testObjectTwo
    testObjectTwo @ testPlayer @ setown
    { testPlayer @ nextowned dup nextowned dup nextowned }list
    0 array_sort
    { testObjectOne @ testObjectTwo @ #-1 }list
    0 array_sort
    array_compare 0 = and
    if me @ "Test passed." notify then
;
(
BEFORE:@set test.muf=W
)
