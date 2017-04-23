: main
    1
    "" striplead "" strcmp not and
    "  \rfoo  " striplead "foo  " strcmp not and
    "           bar" striplead "bar" strcmp not and
    "x" striplead "x" strcmp not and
    if me @ "Test passed." notify then
;
