: main
begin 0 try prog #1 "foo" interp catch pop endcatch repeat
;
(
BEFORE:@tune max_nested_interp_loop_count=25
BEFORE:@set test.muf=!D
EXPECT:interp loop nested
TIMEOUT:20
)
