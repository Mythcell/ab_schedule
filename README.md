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
The default configuration *should* yield a suitable schedule within around 15 minutes.

The code is designed to be as general as possible, and can easily be adapted
to suit any use-case involving assigning pairs amongst a group of people.
One simple example of this is creating a secret santa list – whereby everyone
is randomly assigned somebody to buy a present for.
