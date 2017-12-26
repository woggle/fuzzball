: main
    "TestUser" "foo" newplayer var! testUser
    #0 "TestRoom" newroom var! testRoom
    testUser @ "_someprop" 42 setprop
    testUser @ "~other/foobar/baz" 50 setprop
    testUser @ "~other/foobar" "test" setprop
    testUser @ testRoom @ setlink
    testUser @ "CopiedUser" "bar" copyplayer var! copiedUser
    testUser @ "TestObject" newobject
    1
    copiedUser @ getlink testRoom @ = and
    copiedUser @ "_someprop" getprop 42 = and
    copiedUser @ "~other/foobar" getprop "test" strcmp not and
    copiedUser @ "~other/foobar/baz" getprop 50 = and
    copiedUser @ "bar" checkpassword 1 = and
    copiedUser @ contents #-1 = and
    copiedUser @ location testRoom @ = and
    #0 contents #-1 = not and
    if me @ "Test passed." notify then
;
(
BEFORE:@set test.muf=W
)
