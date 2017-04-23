: main
    "foo::bar:baz::quux" "::" rsplit
    "quux" strcmp not
    swap "foo::bar:baz" strcmp not and
    "foo:bar" "::" rsplit
    "" strcmp not
    swap "foo:bar" strcmp not and
    and
    if me @ "Test passed." notify then
;
