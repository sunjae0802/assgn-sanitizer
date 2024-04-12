# REPOBEE Assignment Sanitizer

This script "sanitizes" the files of programming assignment. A programming assignment is easiest to
develop if the solution is developed in tandem with the assignment. However, the solution should
*not* exist when given to the students.

[REPOBEE](https://github.com/repobee/repobee-sanitizer) is a set of tools that help instructors
develop such assignments. However, the tools are a bit heavyweight and contains a lot of other
functionality that does not fully match my own process, which is why I extracted the assignment
sanitizer part out.

REPOBEE markers are special strings prepended with the line-comment character (and a single space).

There are three types of REPOBEE markers. The first type is the shred marker,
`REPOBEE-SANITIZER-SHRED` which found will discard the file

The second type is the sanitizer markers, between `REPOBEE-SANITIZER-START` and
`REPOBEE-SANITIZER-END`. This will discard all lines between the two markers.

The third type is the replace markers. Everything between between `REPOBEE-SANITIZER-START` and
`REPOBEE-SANITIZER-REPLACE-WITH` will be discarded, but everything between
`REPOBEE-SANITIZER-REPLACE-WITH` and `REPOBEE-SANITIZER-END` will have their comment character
stripped and kept.

For example, the following file:

```python
#!/usr/bin/python

print("HELLO")
# REPOBEE-SANITIZER-START
print(" World")
# REPOBEE-SANITIZER-REPLACE-WITH
# print(" class")
# REPOBEE-SANITIZER-END
```

will be left with:

```python
#!/usr/bin/python

print("HELLO")
print(" class")
```

Command examples:

```console
# Single-file mode
$ python3 assgn-sanitizer.py solution.c -o assignment.c

# Directory mode
$ python3 assgn-sanitizer.py hw1 -o hw1-sanitized
```
