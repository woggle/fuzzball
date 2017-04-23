: main
    0 try
    "x"    dup   dup   dup   dup   dup   dup   dup   dup   dup   dup
    "%999s %999s %999s %999s %999s %999s %999s %999s %999s %999s %999s"
    fmtstring
    catch
        me @ "Test passed." notify
    endcatch
;
