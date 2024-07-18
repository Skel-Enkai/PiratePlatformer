# PiratePlatformer
This is my second game developed in Pygame. (I followed a tutorial by ClearCode: https://youtu.be/KJpP85tnOKg?si=GdKn6_TCi4yHqr8z, however I've been working on expanding the game)
Almost all the commits on this repository happened after I completed the tutorial and have been either additions or modifications to the project.
The art is by 'Pixel Frog' who released the pixel art for free (under a Public Domain License), I made a small donation to them and this is where to find them: https://pixelfrog-assets.itch.io/

All the files that the game requires are in the Directory 'Game': 'Tiled' is the directory where my save files for the level editor that generates CSV files for game is stored, 'Treasure Hunters' is where the orignial art files I have stored by the artist 'Pixel Frog'. 

I'm using Asyncio and Pygbag to package the game as an APK file so it can be played via on a website I'm hosting. 
That's why all the sound files have a .ogg version as the version of Pygbag I'm using only supports .ogg files for audio,
otherwise severe audio tearing can occur.

I'm not currently actively working on this project, as I have decided to learn OpenGL and focus more on pure graphics programming for the time being.
However, sometimes I might add a new enemy or feature for fun. Who knows I migth even turn this into a complete game one day :D

Also of some note: I am aware it would have been far more effecient (in terms of file size) to store my animations as sprite sheets and then process them on load. However, I have already cut up all the images into seperate .png files, and I am loading them individually. I have too many other features planned, so I may get back to this later. 
