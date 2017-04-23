: main
    {
        {
            "the_thing" "x"
        }dict
        {
            "the_thing" "x" "%999s" fmtstring
        }dict
    }list
    "%[the_thing]s %[the_thing]s %[the_thing]s %[the_thing]s %[the_thing]s %[the_thing]s %[the_thing]s "
    "%[the_thing]s %[the_thing]s %[the_thing]s %[the_thing]s %[the_thing]s %[the_thing]s %[the_thing]s" strcat
    2 try array_fmtstrings catch
        me @ "Test passed." notify
    endcatch
;
