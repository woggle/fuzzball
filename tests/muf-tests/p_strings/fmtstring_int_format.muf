: main
    1
    42 "%i" fmtstring "42" strcmp not and
    42 "%3i" fmtstring " 42" strcmp not and
    42 "%03i" fmtstring "042" strcmp not and
    42 "%-3i" fmtstring "42 " strcmp not and
    42 "%|4i" fmtstring " 42 " strcmp not and
    if me @ "Test passed." notify then
;
