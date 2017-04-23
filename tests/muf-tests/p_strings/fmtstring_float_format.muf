: main
    1
    42.0 "%f" fmtstring "42.000000" strcmp not and
    42.0 "%10f" fmtstring " 42.000000" strcmp not and
    42.0 "%.1f" fmtstring "42.0" strcmp not and
    42.0 "%5.1f" fmtstring " 42.0" strcmp not and
    42.0 "%|6.1f" fmtstring " 42.0 " strcmp not and
    42.0 "%03.0f" fmtstring "042" strcmp not and
    42.0 "%-3.0f" fmtstring "42 " strcmp not and
    42.0 "%|4.0f" fmtstring " 42 " strcmp not and
    pi "%4.2f" fmtstring "3.14" strcmp not and
    42.0 "%.1e" fmtstring "4.2e+01" strcmp not and
    42.0 "%.0e" fmtstring "4e+01" strcmp not and
    42.0 "%|7.0e" fmtstring " 4e+01 " strcmp not and
    42.0 "%|4.0e" fmtstring "4e+01" strcmp not and
    if me @ "Test passed." notify then
;
