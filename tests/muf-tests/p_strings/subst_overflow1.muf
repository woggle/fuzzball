: main
    0 try
        "foobar" begin "barquux" "bar" subst repeat
    catch "overflow" instring if me @ "Test passed." notify then endcatch
;
