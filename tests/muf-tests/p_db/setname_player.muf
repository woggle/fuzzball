: main
    1
    "TestPlayer" "dumbpassword" newplayer var! testPlayer
    0 try testPlayer @ "NewName" setname catch
        "requires password" instring and
    endcatch
    0 try testPlayer @ "One dumbpassword" setname catch
        "can't give a player that name" instring and
    endcatch
    0 try testPlayer @ "NewName wrongpassword" setname catch
        "Incorrect password" instring and
    endcatch
    testPlayer @ name "TestPlayer" strcmp not and
    testPlayer @ "NewName dumbpassword" setname
    testPlayer @ name "NewName" strcmp not and
    if me @ "Test passed." notify then
;
(
BEFORE:@set test.muf=W
)
