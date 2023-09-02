# PiratePlatformer
This is my second game developed in Pygame. (I followed a tutorial by ClearCode, however I've been working on expanding the game)
Almost all of the commits on this repository happened after I completed the tutorial and have been either additions or modifications to the project.
The art is by 'Pixel Frog' who released the pixel art for free (under a Public Domain License), I made a small donation to them and this is where to find them: https://pixelfrog-assets.itch.io/

All the files that the game requires are in the Directory 'Game': 'Tiled' is the directory where my save files for the level editor that generates CSV files for game is stored, 'Treasure Hunters' is where the orignial are files I have stored by the artist 'Pixel Frog'. 

I am packaging the application as an APK file with Pygbag (in order to run the game in Web Browsers), so all my code files have to be in the same directory or Pygbag does not seem to recognise them and compile them into bytecode. 
This makes the structure pretty messy, but I haven't found a fix for it just yet.

Also of some note is I am aware it would have been far more effecient (in terms of file size) to store my animations as sprite sheets and then process them on load. However, I have already cut up all the images into seperate .png files and am loading them individually. I have too many other features planned, so I may get back to this later. 
