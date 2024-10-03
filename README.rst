Scheduling ParslFest 2024 with Z3
=================================

For the past 6 years, we have run a meetup of 30-100 participants, `ParslFest <http://parsl-project.org/parslfest.html>`_.

The core is a whole lot of 10 minute lightning talks, scheduled into around 5 sessions over 2 half days, along with over the years some experimentation with different formats of add-on (longer talks, hack sessions, me rambling in front of a terminal for 3 hours).

In previous years we have scheduled those lightning talks by hand directly in the HTML programme. Scheduling has been subject to two constraints: hard constraints on participant availability (in person: if only attending one of the two days, and remotely: being in a timezone-compatible slot) and a softer constraint of trying to group talks into themes.

Manual scheduling has felt increasingly fragile to me: we did not write down people's hard constraints in any one place, instead relying on individual organisers noticing violations; and the softer grouping constraint was mostly ignored because it interacted in too-complicated ways with the hard constraints.

One evening a couple of weeks before ParslFest, I was reading about the `Z3 Theorem Prover <https://github.com/Z3Prover/z3>`_ and was in the mood to try it out against the ParslFest 2024 programme.

This git repository is the result of that.

Run this code
=============


.. code-block::

  $ pip install z3-solver
  $ python scheduler.py 

