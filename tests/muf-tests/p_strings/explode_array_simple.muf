: main
    "foo::::bar::baz::quux" "::" explode_array
    { "foo" "" "bar" "baz" "quux" }list
    array_compare 0 =
    if me @ "Test passed." notify then
;
