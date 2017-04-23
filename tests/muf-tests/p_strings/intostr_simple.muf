lvar localVarNumberZero
: main
    1
    1 intostr "1" strcmp not and
    #1 intostr "1" strcmp not and
    1.0 intostr strtof 1.0 = and
    me intostr "0" strcmp not and
    localVarNumberZero intostr "0" strcmp not and
    { }list 1 try intostr pop 0 and catch pop 1 and endcatch
    if me @ "Test passed." notify then
;
