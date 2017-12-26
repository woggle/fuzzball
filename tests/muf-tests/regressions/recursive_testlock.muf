: main
"test.muf" match "%d" fmtstring
me @ swap PARSELOCK TESTLOCK 
;
(
EXPECT:limit
TIMEOUT:5
)
