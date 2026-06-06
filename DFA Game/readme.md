Contains dfa.py module for parsing a DFA configuration (e.g. level1.txt, level2.txt etc.), 4 level .txt configuration files and main.py that runs the following game:

!!! To play the game, you must input a string containing only the characters N/S/E/W, representing the cardinal directions !!!

The map is as follows:
```
  garden - - - dining - - - kitchen
    |                          |
    |         library - - - hallway - - - start         
heaven/hell   
```
In configuration 1 (level1.txt), you win the game if you successfully travel from start to heaven (hell is not possible in this level).

In configuration 2 (level2.txt), library contains a potion, which can be picked up with input P and dropped in any room with input D. You will go to heaven if you travel to the end holding the potion; otherwise, you will end the game in hell.

Configuration 3 (level3.txt) is similar to configuration 2, except for the fact that you can pick up the potion from the room you left it in.

In configuration 4 (level4.txt), dining contains a key, which can be picked up with input K. The potion in library now requires you to have the key to pick it up. After that, the outcome is identical to configuration 3.
