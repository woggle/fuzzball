: main
    { 1 #0 3.0 "test" }list array_interpret
    "1Room Zero3.0test" strcmp not if
      me @ "Test passed." notify
    else
      me @ "Test failed." notify
    then
;
