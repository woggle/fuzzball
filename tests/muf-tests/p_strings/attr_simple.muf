: main
    1
    "foo" "reset" textattr "\[[0mfoo\[[0m" strcmp not and
    "foo" "normal" textattr "\[[0mfoo\[[0m" strcmp not and
    "foo" "red,bg_black,reverse" textattr "\[[31m\[[40m\[[7mfoo\[[0m" strcmp not and
    "foo" "black,bg_red,bold" textattr "\[[30m\[[41m\[[1mfoo\[[0m" strcmp not and
    "foo" "green,bg_green,dim" textattr "\[[32m\[[42m\[[2mfoo\[[0m" strcmp not and
    "foo" "yellow,bg_yellow,italic" textattr "\[[33m\[[43m\[[3mfoo\[[0m" strcmp not and
    "foo" "blue,bg_blue,underline" textattr "\[[34m\[[44m\[[4mfoo\[[0m" strcmp not and
    "foo" "magenta,bg_magenta,ostrike" textattr "\[[35m\[[45m\[[9mfoo\[[0m" strcmp not and
    "foo" "cyan,bg_cyan,flash" textattr "\[[36m\[[46m\[[5mfoo\[[0m" strcmp not and
    "foo" "white,bg_white,overstrike" textattr "\[[37m\[[47m\[[9mfoo\[[0m" strcmp not and
    if me @ "Test passed." notify then
;
