# ab_schedule
Code to generate author schedules for [Astrobites](https://astrobites.org/).
***

### Requirements

- Python 3.X with numpy

### Getting Started

See the Jupyter notebook for a brief overview of the code.
The examples folder contain several example schedules (as csv).

In a typical Astrobites schedule, each author must write and edit exactly **N** posts.
There are also several other constraints, e.g. authors shouldn't write in consecutive weeks.
The code attempts to construct a schedule on a block-by-block basis (here a *block* can be thought
of as a week, but it is intended to be of arbitrary length), by randomly assigning writers and
editors from global pools. This iterative / brute force approach works well when the number of authors is high
relative to the block size and, of course, for sensible values in the other parameters.
The default configuration *should* yield a suitable schedule within around 15 minutes.
