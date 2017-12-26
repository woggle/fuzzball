: main
    1
    "TestWizard" match "wizard" flag? 0 = and
    "TestWizard" match "truewizard" flag? 1 = and
    if me @ "Test passed." notify then
;
(
BEFORE:@set test.muf=W
BEFORE:@pcreate TestWizard=foobar
BEFORE:@set TestWizard=W
BEFORE:@force TestWizard=@set me=Q
)
