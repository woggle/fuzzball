: main
    0 try
        "" begin
            "more" strcat
        repeat
    catch "overflow" instring if me @ "Test passed." notify then endcatch
;
