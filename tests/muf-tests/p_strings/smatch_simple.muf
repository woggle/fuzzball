: main
    1
    "" "" smatch and
    "foobar" "FOOBAR" smatch and
    "foobar" "foobaz" smatch not and
    "foobar" "*b?r" smatch and
    "foobar" "*b?z" smatch not and
    "foobar" "{foo}bar" smatch not and
    "foo bar" "{foo|baz} bar" smatch and
    "baz bar" "{foo|baz} bar" smatch and
    "foo bar" "{foo}*" smatch and
    "foobar" "{foo}*" smatch not and
    "foobarbaz" "[a-g]oo*" smatch and
    "foobarbaz" "[^e]oo*" smatch and
    "foobarbaz" "[^f]oo*" smatch not and
    "^foo{bar}" "\\^foo?bar\\}" smatch and
    if me @ "Test passed." notify then
;
