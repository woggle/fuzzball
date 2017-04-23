: main
    1
    "" md5hash "d41d8cd98f00b204e9800998ecf8427e" strcmp not and
    "test" md5hash "098f6bcd4621d373cade4e832627b4f6" strcmp not and
    "test\r" md5hash "1fd94de8c776d546d46902d35a437fe2" strcmp not and
    if me @ "Test passed." notify then
;
