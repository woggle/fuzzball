: main
    "foo::bar:baz::quux" "::" split
    "bar:baz::quux" strcmp not
    swap "foo" strcmp not and
    "foo:bar" "::" split
    "" strcmp not
    swap "foo:bar" strcmp not and
    and
    if me @ "Test passed." notify then
;
