: main
    { 1 #2 3.0 "test" }list ":" array_join
    "1:#2:3.0:test" strcmp not if
      me @ "Test passed." notify
    else
      me @ "Test failed." notify
    then
;
