: main
    "foo::::bar::baz::quux" "::" explode
    array_make
    { "quux" "baz" "bar" "" "foo" }list
    array_compare 0 =
    if me @ "Test passed." notify then
;
