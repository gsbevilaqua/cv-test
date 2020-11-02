# cv-test

to run just execute the warp_and_find_checkers.py script with the input folder with samples and the output folder path:
```bash
python warp_and_find_checkers.py bgsamples output
```

### i. How well do you expect this to work on other images?

  Fairly well on images with good enough quality and without extreme perspectives of the board. With maybe missing a few of the checkers.

### ii. What are possible fail cases of this approach and how would you address them?

  I believe on extreme perspectives photos of the board it may distort the checkers enough so that it starts finding double checkers, due to the checker's edge, messing up the final counts.

### iii. How would you implement finding the colors of the checkers and distinguishing which player the checker belongs to?

  For each circle found just take the average of the pixels inside it to know if its a white checker or a black one. In a general sense for when checkers are of a different color than black/white and the colors are not annotated for each sample maybe would do k-means with 2 clusters.
