: main
    1
    #0 player? not and
    #0 thing? not and
    #0 room? and
    #0 program? not and
    #0 exit? not and
    #0 ok? and
    #1 player? and
    #1 thing? not and
    #1 room? not and
    #1 program? not and
    #1 exit? not and
    #1 ok? and
    prog player? not and
    prog thing? not and
    prog room? not and
    prog program? and
    prog exit? not and
    prog ok? and
    if me @ "Test passed." notify then
;
(
BEFORE:@set test.muf=W
)
