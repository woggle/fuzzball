: main
  { 1 "two" 3.0 4 5 6 }list
  array_explode
  6 =
  swap 6 = and
  swap 5 = and
  swap 5 = and
  swap 4 = and
  swap 4 = and
  swap 3 = and
  swap 3.0 = and
  swap 2 = and
  swap "two" strcmp not and
  swap 1 = and
  swap 1 = and
  if
    me @ "Test passed." notify
  else
    me @ "Test failed." notify
  then
;
