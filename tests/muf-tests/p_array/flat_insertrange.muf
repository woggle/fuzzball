: main
  { 1 "two" 3.0 4 5 6 }list
  2 { "foo" "bar" }list array_insertrange
  { 1 "two" "foo" "bar" 3.0 4 5 6 }list array_compare 0 =
  if
    me @ "Test passed." notify
  else
    me @ "Test failed." notify
  then
;
