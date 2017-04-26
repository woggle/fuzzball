: main
0 0 try begin dup ""swap over strcmp while repeat catch "0"if main then endcatch
;
(
EXPECT:overflow
)
