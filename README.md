# ab_schedule
Code to generate author schedules for [Astrobites](https://astrobites.org/).
***

### Requirements

- Python 3.X with numpy

### Schedule

See the Jupyter notebook for a brief overview of the code.
The examples folder contain several example schedules (as csv).

This code creates schedules by populating a list with tuples containing
pairs of author initials, to be interpreted as the writer and editor of an Astrobites post. The full schedule contains a list of these *blocks*.

In a typical Astrobites schedule, each author must write and edit exactly **N** posts (by default, **N** is 3).
There are also several other constraints, e.g. authors shouldn't write in consecutive weeks, authors shouldn't write and edit in the same week, etc.
The code attempts to construct a schedule on a block-by-block basis (here a *block* can be thought
of as a week, but it is intended to be of arbitrary length), by randomly assigning writers and
editors from global pools. This iterative / brute force approach works well when the number of authors is high
relative to the block size and, of course, for sensible values in the other parameters.
The default configuration *should* yield a suitable schedule within around 5-10 minutes, no more than 15.

The code is designed to be as general as possible, and can easily be adapted
to suit any use-case involving assigning pairs amongst a group of people.
One simple example of this is creating a secret santa list – whereby everyone
is randomly assigned somebody to buy a present for.

### NB: Authors and Block Sizes

Suppose we have 10 authors: `A, B, C, D, ...` up to `J`. Given this, the maximum block size under the default constraints is 2.
This is since, ideally, no author should write or edit in consecutive weeks. One example schedule could be as follows:
```
(C,F)
(A,G)

(E,D)
(B,H)
```
from which it should be clear that if the block size was 3, then two authors would be scheduled twice in consecutive blocks.
It is thus important to ensure that the number of authors is **greater than `4*block_size`**, in which case you may need to lower `num_regular`.
