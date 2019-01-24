# lightshapes
This is a fun little side project that I did for a party. It uses a projector to project animations on cardboard shapes like so:

![](images/demo.jpg)

To use this:

1. Cut out some shapes (polygons) from white cardboard, hang them up somewhere.
2. Align the projector so that all shapes are covered by its image.
3. Run `python find-polygons.py` and use the cursor to find the edges of your cardboard shapes (arrow keys to move, space to set edge, return to go to next polygon).
4. Run `python animate.py` to start the animations. Some of them are controlled by the music, so make sure your laptop mic is not covered up.
