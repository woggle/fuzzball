: main 
    { 1 2 3 }list ARRAY_PIN var! x
    { 4 5 6 }list ARRAY_PIN var! y
    x @ y @ 0 ARRAY_SETITEM POP
    y @ x @ 0 ARRAY_SETITEM POP
    x @ y @ ARRAY_COMPARE
;
(
EXPECT:
)
