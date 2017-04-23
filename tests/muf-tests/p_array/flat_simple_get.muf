: main
  { 1 "two" 3.0 4 5 6 }list
  dup 0 array_getitem 1 = 
  over 1 array_getitem "two" strcmp not and
  over 2 array_getitem 3.0 = and
  over array_count 6 = and
  over array_last swap 5 = and and
  over array_first swap 0 = and and
  over 3 array_next 1 = swap 4 = and and
  over 3 array_prev 1 = swap 2 = and and
  if
    me @ "Test passed." notify
  else
    me @ "Test failed." notify
  then
;
