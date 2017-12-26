: main
    1
    "One" pmatch #1 = and
    "TestPlayer" pmatch #-1 = and
    "TestPlayer" "dumbpassword" newplayer var! testPlayer
    "TestPlayer" pmatch testPlayer @ = and
    testPlayer @ "NewName dumbpassword" setname
    "TestPlayer" pmatch #-1 = and
    "NewName" pmatch testPlayer @ = and
    if me @ "Test passed." notify then
;
(
BEFORE:@set test.muf=W
)
