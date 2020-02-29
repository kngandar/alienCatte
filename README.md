# alienCatte

A small game where you take care of a digital cat pet.

### Contents
***release*** - Builds source code to an exe file. Setup was done by Glennarthyr Gillespie.

***src*** - Contains source code and assets used for the game.


### About development
This project features two important code that I have worked on:
1. Animation layer
2. Game logic


#####  Animation layer
I found the arcade library to be lacking in its displaying animation functionalities.
So prior to actually working on the game, I tried to make a mini-library/layer which I have called 'Animation'.
It has a layered architecture and there are documentations within the files themselves.

If you would like to see the details, I would recommend checking out ***src/animation.py*** first.
Related python files includes: ***subClasses.py***, ***baseClasses.py*** and ***functions.py***


##### Game logic
For the game itself, ***src/main.py*** displays the different views/scenes in the game and initializes the assets and logic.
The actual game algorithm can be found in ***src/pentacatLogic.py***.
