: main
  { 1 "two" 3.0 4 5 6 }list
  2 3  array_delrange
  { 1 "two" 5 6 }list array_compare 0 =
  if
    me @ "Test passed." notify
  else
    me @ "Test failed." notify
  then
;
