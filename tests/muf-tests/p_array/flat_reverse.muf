: main
  { 1 "two" 3.0 4 5 6 }list
  array_reverse
  dup 1 array_getitem 5 = 
  swap 4 array_getitem "two" strcmp not and
  if
    me @ "Test passed." notify
  else
    me @ "Test failed." notify
  then
;
