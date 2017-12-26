: main
0 var! c
begin 0 try
" TIMESPLIT 000 ARR"begin dup "r"STRENCRYPT FMTSTRING while repeat catch endcatch
c @ 1 + dup c ! 500 = not while
repeat
;
(
BEFORE:@set test.muf=!D
EXPECT:
TIMEOUT:20
)
