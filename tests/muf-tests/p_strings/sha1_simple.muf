: main
    1
    "" sha1hash "da39a3ee5e6b4b0d3255bfef95601890afd80709" strcmp not and
    "test" sha1hash "a94a8fe5ccb19ba61c4c0873d391e987982fbbd3" strcmp not and
    "test\r" sha1hash "923f760def6227e59cf25c6feaef8a2598a5de97" strcmp not and
    if me @ "Test passed." notify then
;
