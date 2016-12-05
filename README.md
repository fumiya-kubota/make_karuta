This script will create the image, such as the following image.

![1](https://cloud.githubusercontent.com/assets/2044262/20872693/e1c3a718-bae3-11e6-820d-c187f8bd90c2.png)


## Usage:
```
Usage: services.py [OPTIONS] BG

Options:
  --paper_size [A0|A1|A2|A3|A4|A5|A6|B0|B1|B2|B3|B4|B5|B6]
  --resolution INTEGER
  --karuta_size <INTEGER INTEGER>...
  --dist TEXT
  --help 
```

## arguments:
"BG" Please specify the path of the image of the frame.

## Options:
For "paper_size", please select the paper size to use when printing.
"resolution" should specify the resolution, ie pixel per inch (default is 200).
"karuta_size" is the size of a single karuta. Please specify units in millimeters, width, height.
"dist" is the output destination directory.
