: main
  { 1 "two" 3.0 4 5 6 }list
  1 3 array_getrange
  { "two" 3.0 4 }list array_compare 0 =
  if
    me @ "Test passed." notify
  else
    me @ "Test failed." notify
  then
;
