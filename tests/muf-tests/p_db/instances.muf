: main
    1
    prog instances 1 = and
    "tempprogram.muf" newprogram var! testprog
    testprog @ instances 0 = and
    if me @ "Test passed." notify then
;
(
BEFORE:@set test.muf=W
)
