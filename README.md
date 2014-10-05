image-clustering
================

hybrid system for similar images clustering


The purpose of this project is to develop a hybrid system for grouping similar images from large collections of images, such as those returned by image search engines. This approach involves extracting low-level features of images (e.g., dominant colors and image entropy) and combining them with the high-level characteristics, represented by keywords and annotations; then, the K-means clustering algorithm and the Self Organizing Maps artificial neural network were used, with different metrics, to cluster the images. Next, a series of tests was conducted to compare the efficiency of the two algorithms and the quality of the results.

A proof of concept webpage can be found here: http://imageclustering.herokuapp.com/ (When asked for worker id, just insert anything you want). It is a 'find the intruder' game meant to test the quality of the clusters obtained.