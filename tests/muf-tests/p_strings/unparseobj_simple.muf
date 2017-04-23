: main
    1
    #1 unparseobj "One(#1PWM3)" strcmp not and

    #0 "Test Object" newobject
    dup "V" set
    dup "Z" set
    unparseobj
    "Test Object(#4VZ)" strcmp not and

    #-1 unparseobj "*NOTHING*" strcmp not and

    #400 unparseobj "*INVALID*" strcmp not and

    #-4 unparseobj "*NIL*" strcmp not and

    #-3 unparseobj "*HOME*" strcmp not and

    if me @ "Test passed." notify then
;
