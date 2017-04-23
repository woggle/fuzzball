: main
    "x" "%999s" fmtstring
    1 try
    dup    dup   dup   dup   dup   dup   dup   dup   dup   dup   dup
    "%s %s %s %s %s %s %s %s %s %s %s"
    fmtstring
    catch
        me @ "Test passed." notify
    endcatch
;
