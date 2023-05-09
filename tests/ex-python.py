#!/usr/bin/python

    print("HELLO")
    #REPOBEE-SANITIZER-START
    print(" World")
    #REPOBEE-SANITIZER-REPLACE-WITH

    #print(" class")

    #REPOBEE-SANITIZER-END
