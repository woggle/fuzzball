:  main
#0 "0" newroom #0 moveto
#0 "obj1"newexit var! x2
"obj1"match RECYCLE #0 "exit2"newexit PROG var! x4
"0"match x2 @ x4 @ SETLINK #0 "obj1"newobject var! x3
x3 @ "exit2"FORCE main
;
(
BEFORE:@set test.muf=W
BEFORE:@set test.muf=!D
BEFORE:@tune max_process_limit=5
EXPECT:
)
