: main
  { 1 "two" 3.0 4 5 6 }list
  3  array_cut
  swap
  { 1 "two" 3.0 }list array_compare 0 =
  swap
  { 4 5 6 }list array_compare 0 = and
  if
    me @ "Test passed." notify
  else
    me @ "Test failed." notify
  then
;
