: main
    1
    "ab" "%s" fmtstring "ab" strcmp not and
    "ab" "%3s" fmtstring " ab" strcmp not and
    "ab" "%-3s" fmtstring "ab " strcmp not and
    "ab" "%|4s" fmtstring " ab " strcmp not and
    if me @ "Test passed." notify then
;
