# BaceQG - Boolean Algebra Circuit and Expression Question Generator

## Brief

BaceQG is a boolean algebra question maker for classes including but not limited to machine structure, digital design, and other classes that take boolean algebra as an important concept. 

Before BaceQG, logic simplification questions are generally handicrafted. Experienced instructors come up with an expression, complicate them, and then put it in the exam. However, as computer-based testing is more and more prominent, boolean algebra questions do not support the next-variant feature, as all student get the same circuit picture and they then simplify them down to the same expression.

Additionally, BaceQG is great for generating student exercises, because you can configure the student exercises to have the same level of difficulty and give them hundreds of different circuits on their demand, to make sure they're prepared for that difficulty level.

## Dependencies

BaceQG requires the following dependencies to run:
* python 3.6 or higher, for f string features
* pyyaml, for reading the config.yaml file
* schemdraw, for drawing the circuit diagram from expression
  
Additionally, apllo adapted the "boolean.py" library and included it as the boolean.py file in the repository, because it extensively used it throughout and it is best to keep it in the repo. However, everything in the boolean.py file is NOT written by me and should be credited to https://github.com/bastikr/boolean.py and all its contributers. 

## Configuring

The generation of BaceQG follows the config.yaml file, with the following specification:

* `de_morgan`: (1 or 0) whether or not the De Morgan's Law is used to complicate the logic
* `trials`: (int) the number of times BaceQG will attempt to generate the logic expression
* `input_num`: (int) the true number of inputs to the simpliest expression
* `dummy`: (int) the number of symbols present in the final question expression but is eliminated in the simplest form
* `drawing`: (1 or 0) whether or not BaceQG should generate the circuit diagram 
* `print`: (1 or 0) whether or not BaceQG should print the final logical expression 