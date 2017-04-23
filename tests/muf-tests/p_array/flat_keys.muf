: main
  { 1 "two" 3.0 4 5 6 }list
  array_keys
  6 =
  swap 5 = and
  swap 4 = and
  swap 3 = and
  swap 2 = and
  swap 1 = and
  swap 0 = and
  if
    me @ "Test passed." notify
  else
    me @ "Test failed." notify
  then
;
