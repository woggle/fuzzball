: main
    1
    "" 0 strcut "" strcmp not swap "" strcmp not and and
    "foobar" 3 strcut "bar" strcmp not swap "foo" strcmp not and and
    "foo" 3 strcut "" strcmp not swap "foo" strcmp not and and
    "foo" 4 strcut "" strcmp not swap "foo" strcmp not and and
    "foobar" 0 strcut "foobar" strcmp not swap "" strcmp not and and
    if me @ "Test passed." notify then
;
