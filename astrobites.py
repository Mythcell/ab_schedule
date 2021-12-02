"""
===============================================================================
Code to generate schedules for Astrobites
Copyright (C) 2021 Mitchell Cavanagh

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>
===============================================================================

This code contains methods to generate schedules for Astrobites.

Typical usage:
    schedule = Schedule()
    blocks, queue_posts, beyond_posts = schedule.make_schedule()
"""

import numpy as np


class Schedule(object):
    """Class containing methods for creating an Astrobites schedule.

    Attributes:
        authors (List[str]): List of authors
    """

    def __init__(self, authors=[], f_authors='authors.txt'):
        """Base constructor.

        Initialises a Schedule class object either with the provided list of
        authors initials, or a filepath to a list of authors initials.
        The default filepath is 'authors.txt'. Ensure the file contains
        author initials separated by newlines.

        Args:
            authors (List[str]): List of author initials
            f_authors (str): Path to file containing author initials
        """

        self.authors = authors if authors else list(
            np.loadtxt(f_authors, dtype=str))


    def validate_schedule(self, blocks, num_writes=3):
        """Double-checks the provided schedule to ensure it is valid.

        This code checks to make sure each author writes and edits exactly
        three times, and that no author has to write in successive blocks.

        Args:
            blocks (List[List[(str,str)]]): List of blocks of writer-editor tuples
            num_writes (int): Number of times each author should write and edit.

        Returns:
            True if the schedule is valid, False otherwise
        """
        wc = {a: 0 for a in self.authors}
        ec = {a: 0 for a in self.authors}

        wprev, eprev = set(), set()
        for _, b in enumerate(blocks):
            wseen, eseen = set(), set()
            for w, e in b:
                if w == e:
                    print('Error: Writes and edits same post ({},{})'.format(w, e))
                    return False
                if w in wprev:
                    print('Error: back-to-back write ({})'.format(w))
                    return False
                if e in eprev:
                    print('Error: back-to-back edit ({})'.format(e))
                    return False
                # Code to enforce writers not having previously edited or
                # editors not having previously written.
                # CURRENTLY DISABLED AS PER GENERATE_SCHEDULE
                # if w in eprev:
                #     print('Error: {} was a previous editor'.format(w))
                #     return False
                # if e in wprev:
                #     print('Error: {} was a previous writer'.format(e))
                #     return False
                wc[w] += 1
                ec[w] += 1
                wseen.add(w)
                eseen.add(e)
            # rollover current writes and edits
            wprev = set(wseen)
            eprev = set(eseen)

        # check to make sure all writer counts are equal to [num_writes]
        if set(wc.values()) != {num_writes}:
            print('Error, not all authors write exactly', num_writes, 'times')
            return False
        # this step can logically be omitted, but good to double-check regardless
        if set(ec.values()) != {num_writes}:
            print('Error, not all authors edit exactly', num_writes, 'times')
            return False

        # otherwise schedule is (hopefully) valid
        return True


    def generate_schedule(self, num_writes=3, block_size=7, verbose=False, max_iter=200000):
        """Generate a suitable Astrobites schedule.

        This code will attempt to randomly assign editors and writers into
        blocks of size up to [block_size], such that each writer writes
        [num_writes] times (and each editor edits [num_writes] times). This code
        also aims to avoid instances of back-to-back writes and edits. As there
        is a high degree of randomisation involved, this code may take a while
        to execute (generally less than 100 trials, but potentially up to 300).
        Note this function is meant to be called within a loop, i.e. make_schedule().

        Args:
            num_writes (int): Number of posts each author should write and edit
            block_size (int): The maximum number of writer/editor pairs to assign
                for each block
            verbose (bool): Whether to output debug print lines
            max_iter (int): Maximum number of attempts to generate a valid schedule.

        Returns:
            blocks (List[List[Tuple[str,str]]]): A list of blocks,
                where each block is a list of (write,edit) tuples.
        """
        # Determine number of blocks to create
        # num_posts = len(self.authors)*num_writes
        # num_blocks = int(np.ceil(num_posts // block_size))

        # Create separate pools of writers and editors
        writer_pool, editor_pool = [], []
        for a in self.authors:
            writer_pool.extend([a]*num_writes)
            editor_pool.extend([a]*num_writes)
        # Not strictly necessary, I found this to slightly improve running times
        np.random.shuffle(writer_pool)
        np.random.shuffle(editor_pool)

        # Setup some dictionaries to keep track of write/edit counts
        wc = {a: 0 for a in self.authors}
        ec = {a: 0 for a in self.authors}

        # Keep track of iterations
        iter = 0

        blocks = []
        # This is to keep track of writers and editors from the previous block
        prev_writers = set()
        prev_editors = set()

        # Process blocks
        while len(writer_pool) > 0:

            if verbose:
                print('{} left ({})'.format(len(writer_pool), iter))

            pairs = []
            frozen_writers = set()
            frozen_editors = set()

            # Main selection loop
            while True:
                iter += 1
                # Break if we've exceeded the max iterations
                if iter > max_iter:
                    return -1

                # select some writers and editors from their respective pools
                writers = min(list(writer_pool), list(
                    np.random.choice(writer_pool, block_size)))
                editors = min(list(editor_pool), list(
                    np.random.choice(editor_pool, block_size)))

                # ensure all writers and editors are unique
                if len(writers+editors) != len(set(writers+editors)):
                    continue
                # ensure no back-to-back writes
                if len(set(writers) & prev_writers) != 0:
                    continue
                # ensure no back-to-back edits
                if len(set(editors) & prev_editors) != 0:
                    continue
                # ensure no back-to-back writes or edits
                # COMMENTED OUT AS THIS RESULTS IN BLOWOUTS TO GENERATION TIMES
                # if len((set(writers) | set(editors)) & (prev_writers | prev_editors)) != 0:
                #     continue
                # otherwise can proceed as normal
                break

            # Process writer/editor pairs
            for w, e in zip(writers, editors):
                pairs.append((w, e))
                # Freeze these writers and editors so that
                # they are not chosen for the next block
                frozen_writers.add(w)
                frozen_editors.add(e)
                # Remove entries from the writer pool
                writer_pool.remove(w)
                editor_pool.remove(e)
                # Keep track of the number of writes/edits
                wc[w] += 1
                ec[e] += 1

            blocks.append(pairs)
            # Keep track of who wrote and edited
            prev_writers = set(frozen_writers)
            prev_editors = set(frozen_editors)

        # Make sure there are no leftovers
        if len(writer_pool) != 0 or len(editor_pool) != 0:
            return -1
        # Make sure everyone writes the same number of times
        if len(set(wc.values())) != 1:
            return -1
        # Lastly, do a final validation
        if not self.validate_schedule(blocks, num_writes):
            return -1
        # All shall be well, and all manner of things shall be well
        return blocks


    def write_schedule(self, blocks, queue_posts, beyond_posts,
                       num_queue=1, num_beyond=1, first_day='Sunday',
                       beyond_day='Friday', f_out='schedule.csv'):
        """Write the schedule to a csv file.

        The output file has the following columns:
            week_num, day, writer, editor, post_type
        Note: post_type is omitted if the post is regular

        By default, queue posts are assigned to the first day.
        Multiple queue/beyond posts are stacked on their respective days.
        NOTE: This is designed for 7-day blocks

        Args:
            blocks (List[List[Tuple[str,str]]]): The schedule
                (i.e. list of lists of writer-editor tuples)
            queue_posts (List[Tuple[str,str]]): List of queue posts
            beyond_posts (List[Tuple[str,str]]): List of beyond posts
            num_queue (int): Number of queue posts per schedule block
            num_beyond (int): Number of beyong posts per schedule block
            first_day (str): When to start the week
                (queue posts are also scheduled for this day)
            beyond_day (str): When to schedule the beyond posts
            f_out (str): Name of the output file
        """

        days = ['Sunday', 'Monday', 'Tuesday',
                'Wednesday', 'Thursday', 'Friday', 'Saturday']
        first_day_index = days.index(first_day)
        beyond_day_index = days.index(beyond_day)

        f = open(f_out, 'w')

        for i, b in enumerate(blocks):
            # Note the lists are explicitly copied,
            # so as to ensure that the originals remain unmodified
            postpool = list(b)
            qp = list(queue_posts[i*num_queue:(i+1)*num_queue])
            bp = list(beyond_posts[i*num_beyond:(i+1)*num_beyond])

            # Check to make sure there are actually queue posts to write
            if qp:
                # Remove queue and beyond posts from the postpool
                # this is so postpool only contains regular posts
                for post in qp+bp:
                    postpool.remove(post)
                # write queue posts
                for q in qp:
                    f.write(
                        str(i+1)+','
                        + str(days[first_day_index])+','
                        + str(q[0])+','
                        + str(q[1])+','
                        + 'queue'+'\n'
                    )
                current_day = (first_day_index + 1) % len(days)
            else:
                # Just have regular posts starting on Sunday if there are
                # no queue posts to designate
                current_day = first_day_index

            # now loop through the days
            while len(postpool) > 0:
                # if it's a beyond day
                if current_day == beyond_day_index and len(bp) > 0:
                    # dump all posts onto this day
                    for b in bp:
                        f.write(
                            str(i+1)+','
                            + str(days[current_day])+','
                            + str(b[0])+','
                            + str(b[1])+','
                            + 'beyond'+'\n'
                        )
                    bp = []  # incase we loop back to Friday
                    current_day = (current_day + 1) % len(days)
                    continue

                # otherwise it's a regular day
                pi = np.random.choice(len(postpool))
                f.write(
                    str(i+1)+','
                    + str(days[current_day])+','
                    + str(postpool[pi][0])+','
                    + str(postpool[pi][1])+',\n'
                )
                del postpool[pi]  # remove post from postpool
                # loop to the next day
                current_day = (current_day + 1) % len(days)

        # Finally, close the file
        f.close()
        print('Schedule written to', f_out)


    def get_queue_beyond(self, blocks, block_size, num_writes=3,
                         num_queue=1, num_beyond=1, max_iter=200000):
        """
        Determines queue and beyond posts from the given blocks.
        Note: queue/beyond posts are not selected for incomplete blocks.

        Args:
            blocks (List[List[Tuple[str,str]]]): List of lists of writer-editor pairs
            block_size (int): Maximum size of each block
            num_writes (int): Number of posts each author must write
            num_queue (int): Number of queue posts
            num_beyond (int): Number of beyond posts
            max_iter (int): Maximum iterations to determine queue/beyond posts

        Returns:
            queue_posts (List[Tuple[str,str]]): List of queue posts
            beyond_posts (List[Tuple[str,str]]): List of beyond posts
        """

        queue_posts, beyond_posts = [], []
        # dicts to store counts
        qc = {a: 0 for a in self.authors}
        bc = {a: 0 for a in self.authors}
        iter = 0

        for _, b in enumerate(blocks):
            # Loop for selecting queue/beyond posts
            while True:
                if iter > max_iter:
                    break  # incase it's stuck in an infinite loop
                postlist = list(b)  # copy current block
                qposts, bposts = [], []  # these are temporary lists for each block

                # Skip queue/beyond selection for incomplete blocks
                if len(postlist) < block_size:
                    break

                # Pick queue posts
                qi = np.random.choice(
                    range(len(postlist)), num_queue, replace=False)
                for i in qi:
                    qposts.append(postlist[i])
                for i in sorted(qi, reverse=True):
                    # remove from list to avoid clashing with beyond posts
                    del postlist[i]
                # Pick beyond posts
                bi = np.random.choice(
                    range(len(postlist)), num_beyond, replace=False)
                for i in bi:
                    bposts.append(postlist[i])

                # Make sure no author writes just queue or beyond posts
                valid = True
                if num_queue + num_beyond < num_writes:
                    for post in qposts + bposts:
                        if qc[post[0]] + bc[post[0]] > max(num_writes, 1):
                            valid = False
                            break  # break for loop

                if valid:
                    for post in qposts:
                        qc[post[0]] += 1
                    for post in bposts:
                        bc[post[0]] += 1
                    queue_posts.extend(qposts)
                    beyond_posts.extend(bposts)
                    break  # break main loop
                iter += 1  # otherwise increment iter counter

        # This shouldn't happen, but it's good to have extra protection
        if iter > max_iter:
            print('Unable to determine queue/beyond posts.')
            print('Try lowering num_queue and/or num_beyond, or raising num_writes')

        # Some final debug checks
        # for i in range(len(blocks)-1):
        #     for j in queue_posts[i*num_queue:(i+1)*num_queue]:
        #         assert j in blocks[i]
        #     for j in beyond_posts[i*num_beyond:(i+1)*num_beyond]:
        #         assert j in blocks[i]

        return queue_posts, beyond_posts

    def make_schedule(self, num_writes=3, num_regular=5, num_queue=1,
                      num_beyond=1, max_trials=1000, max_iter=200000,
                      verbose=True, write_csv=True):
        """Make a suitable Astrobites schedule.

        This code runs a series of trials to randomly generate schedules until
        one is found that satisfies the validation requirements. Once a suitable
        schedule is found, this function then selects queue and beyond posts.
        Queue and beyond posts are not chosen for incomplete blocks.

        Args:
            num_writes (int): The number of times each author writes/edits
            num_regular (int): The number of regular posts per block
            num_queue (int): The number of queue posts per block
            num_beyond (int): The number of beyond posts per block
            max_trials (int): The maximum number of trial schedules to generate
            max_iter (int): Maximum number of iterations for each trial
                (see generate_schedule)
            verbose (bool): Whether to print out debug statements (recommended)
            write_csv (bool): Whether to write the schedule to file
                (the output file is named schedule.csv)

        Returns:
            blocks (List[List[Tuple[str,str]]]): The completed schedule
                (list of lists of writer-editor tuples)
            queue_posts (List[Tuple[str,str]]): List of queue posts
            beyond_posts (List[Tuple[str,str]]): List of beyond posts
        """
        blocks = []
        block_size = num_regular + num_queue + num_beyond

        # First get the schedule
        t = 0
        while t < max_trials:
            t += 1
            if verbose:
                print('Trial', t, 'of', max_trials)
            blocks = self.generate_schedule(num_writes=num_writes,
                block_size=block_size, verbose=verbose, max_iter=max_iter)
            if blocks == -1:
                continue
            if t >= max_trials:
                print('Exhausted all trials. Try again and/or maybe increase [max_trials]')
                return None
            # at this point we should have a suitable schedule
            break

        # Now get queue and beyond posts
        queue_posts, beyond_posts = self.get_queue_beyond(blocks, block_size,
            num_queue=num_queue, num_beyond=num_beyond, max_iter=max_iter)

        # Write to file only if flag is True and get_queue_beyond succeeded
        if write_csv and queue_posts and beyond_posts:
            self.write_schedule(blocks, queue_posts, beyond_posts,
                num_queue=num_queue, num_beyond=num_beyond)

        return blocks, queue_posts, beyond_posts


    def make_secret_santa(self, f_out='secret_santa.csv', verbose=False,
                          max_trials=1000, max_iter=200000):
        """Creates a secret santa list.
        Here each writer is paired with exactly one editor.

        Args:
            f_out (str): Output file
            verbose (bool): Whether to print verbose output
            max_trials (int): The maximum number of trials
            max_iter (int): Maximum number of iterations per trial
        """

        t = 0
        while t < max_trials:
            t += 1
            if verbose:
                print('Trial', t, 'of', max_trials)
            blocks = self.generate_schedule(num_writes=1, block_size=1,
                verbose=verbose, max_iter=max_iter)
            if blocks == -1:
                continue
            if t >= max_trials:
                print('Exhausted all trials. Try again and/or maybe increase [max_trials]')
                return None
            break

        with open(f_out,'w') as f:
            for _,i in enumerate(blocks):
                for w,e in i:
                    f.write(str(w)+','+str(e)+'\n')
        print('Saved secret santa to', f_out)


    def export_blocks(self, blocks, f_out='blocks.csv'):
        """Outputs only the block schedule as a csv file.
        Useful for manual inspection.

        The output file has the following columns:
            week_num, writer, editor

        Args:
            blocks (List[List[Tuple[str,str]]]): List of lists of writer-author pairs
            f_out (str): Output file
        """

        with open(f_out, 'w') as f:
            f.write('#block,writer,editor\n')
            for i, b in enumerate(blocks):
                for w, e in b:
                    f.write(
                        str(i)+','
                        + str(w)+','
                        + str(e)+'\n'
                    )


    def randomise_authors(self, num=40, initials_length=2):
        """Debug method to generate random author initials.

        Args:
            num (int): Number of author initials to generate
            initials_length (int): Length of the author initial
        """

        letters = [chr(l+ord('A')) for l in range(26)]
        rand_initials = set()
        while len(rand_initials) < num:
            rand_initials.add(''.join(np.random.choice(
                letters, initials_length, replace=False)))
        self.authors = rand_initials


    def get_authors(self):
        """Returns the list of authors associated with this instance"""
        return self.authors


    def update_authors(self, authors):
        """Updates the list of authors associated with this instance"""
        self.authors = authors


    def list_authors(self):
        """Prints out the list of authors associated with this instance"""
        for a in self.authors:
            print(a)


if __name__ == '__main__':
    test = Schedule()
    #test.randomise_authors(1000,3)
    blocks, queue_posts, beyond_posts = test.make_schedule(verbose=True, max_iter=200000)
    test.make_secret_santa()
    #test.write_schedule(blocks,queue_posts,beyond_posts)
