: main
    #0 "TestRoom" newroom var! testRoom
    #0 "TestThing" newobject var! testObject
    1
    { "dark" "abode" "chown_ok" "guest" "haven" "jump_ok" "link_ok" "kill_ok"
      "mucker" "nucker" "sticky" "wizard" "truewizard" "zombie" }list
    foreach swap pop testRoom @ swap flag? 0 = and repeat
    { "dark" "abode" "chown_ok" "guest" "haven" "jump_ok" "link_ok" "kill_ok"
      "mucker" "nucker" "sticky" "vehicle" "wizard" "truewizard" "xforcible" "zombie" }list
    foreach swap pop testObject @ swap flag? 0 = and repeat
    { "dark" "abode" "color" "guest" "haven" "jump_ok" "link_ok" "kill_ok"
      "sticky" "zombie" "quell" "interactive" }list
    foreach swap pop #1 swap flag? 0 = and repeat
    #1 "mucker" flag? 1 = and
    #1 "nucker" flag? 1 = and
    #1 "wizard" flag? 1 = and
    me @ "interactive" flag? 0 = and
    prog "viewable" flag? and
    prog "silent" flag? not and
    prog "debug" flag? prog "dark" flag? = and
    if me @ "Test passed." notify then
;
(
BEFORE:@set test.muf=W
BEFORE:@set test.muf=V
)
