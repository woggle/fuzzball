: main
    {
        { "name" "One"     "num" 1 }dict
        { "name" "Two"     "num" 2 }dict
        { "name" "Three"   "num" 3 }dict
    }list
    SORTTYPE_DESCENDING "num" ARRAY_SORT_INDEXED
    {
        { "name" "Three"   "num" 3 }dict
        { "name" "Two"     "num" 2 }dict
        { "name" "One"     "num" 1 }dict
    }list
    array_compare 0 =
    if
      me @ "Test passed." notify
    else
      me @ "Test failed." notify
    then
;
