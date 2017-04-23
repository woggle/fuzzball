: main
  "new two"
  { 1 "two" 3.0 4 5 6 }list
  1
  array_insertitem
  dup 1 array_getitem "new two" strcmp not
  swap 2 array_getitem "two" strcmp not and
  if
    me @ "Test passed." notify
  else
    me @ "Test failed." notify
  then
;
