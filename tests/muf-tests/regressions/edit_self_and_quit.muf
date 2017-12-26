: main
    me @ "@edit test.muf" force
    me @ "c" force
    me @ "Test passed." notify
;
(
BEFORE:@set test.muf=W
NOAUTOQUIT:1
AFTER:QUIT
)
