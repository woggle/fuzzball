: main
  { 1 "two" 3.0 4 5 6 }list
  "new two" swap 1 array_setitem
  "new value" swap array_appenditem
  3 array_delitem
  dup 0 array_getitem 1 = 
  over 1 array_getitem "new two" strcmp not and
  over 2 array_getitem 3.0 = and
  over 3 array_getitem 5 = and
  over 5 array_getitem "new value" strcmp not and
  over array_count 6 = and
  over array_last swap 5 = and and
  if
    me @ "Test passed." notify
  else
    me @ "Test failed." notify
  then
;
