Scheduling ParslFest 2024 with Z3
=================================

For the past 6 years, we have run a meetup of 30-100 participants, `ParslFest <http://parsl-project.org/parslfest.html>`_.

The core is a whole lot of 10 minute lightning talks, scheduled into around 5 sessions over 2 half days, along with over the years some experimentation with different formats of add-on (longer talks, hack sessions, me rambling in front of a terminal for 3 hours).

In previous years we have scheduled those lightning talks by hand directly in the HTML programme. Scheduling has been subject to two constraints: hard constraints on participant availability (in person: if only attending one of the two days, and remotely: being in a timezone-compatible slot) and a softer constraint of trying to group talks into themes.

Manual scheduling has felt increasingly fragile to me: we did not write down people's hard constraints in any one place, instead relying on individual organisers noticing violations; and the softer grouping constraint was mostly ignored because it interacted in too-complicated ways with the hard constraints.

One evening a couple of weeks before ParslFest, I was reading about the `Z3 Theorem Prover <https://github.com/Z3Prover/z3>`_ and was in the mood to try it out against the ParslFest 2024 programme.

This git repository is the result of that.

How it works
============

The code defines 35 integer Z3 variables, mapping each of 35 talks to a numbered session.

Near the top of the code, ``talk_titles_prefs`` is an array that maps talk numbers to a human readable description along with some other metadata I will talk about later.

The solution that Z3 outputs is then a tuple of 35 integers, mapping talks to sessions. At the end of the code, this is pretty-printed into something that looks more like the event programme, for human consumption.

Without any further constraints, this doesn't result in a valid programme. For example, it would be legitimate for z3 to map all talks to session 99 which does not exist (and I think what happened was that all talks were mapped to session 0).

The first constraints I added are to do with the structure of the sessions, rather than the constraints I talked about in the introduction:

* each talk must be in a valid session: for example, a talk cannot be scheduled in session 99.

  This was implemented by declaring this constaint 35 times (one for each talk):

  .. code-block::

    And(t >= 1, t <= n_sessions) for t in talk_sessions


* each sessions has a maximum number of talks - because of break placement, the sessions weren't all the same size.

  Z3 lets you declare that out of a collection of boolean statements, no more than a specified maximum may be true, using `AtMost`. For each session, I made 35 boolean statements to check if a talk is in that session, and constrained the maximum number of those statements that could be true.
 
  .. code-block::

    session_sizes = [7,6,6,6,5,6]

    def SessionSize(session, size):
      return AtMost(*[t == session for t in talk_sessions], size)

    sessions_have_sizes = [SessionSize(n+1, session_sizes[n]) for n in range(0,len(session_sizes))]

With these constraints, the code will output a schedule with the right number of talks in each session, but without any of the constraints mentioned in the introduction. This is roughly the same as taking talks from the list and putting them anywhere there is a hole in the schedule.

Now I added in the hard constraints for individual talk timing. This is an explicit list of constraints on numbered talks (or rather, on the Z3 variable mapping a particular talk to a session). The comments next to each talk describe the talk.

There are two functions that give custom constraints: ``OnDay`` knows how to constrain a talk to a particular day (day 1 or day 2) rather than a particular session. It is implemented with an ``if`` statement that generates a bunch of session constraints.

``YaduConstraints`` is a set of constraints over two talks. My colleague Yadu was the only speaker giving two lightning talks and I wanted his talks to be on different days (without constraining which talk went on which day). ``YaduConstraints`` is implemented in terms of ``OnDay`` on both of his talks: either his talk 4 is on day 1 and his talk 23 is on day 2, or the other way round.

  .. code-block::

    special_talk_constraints = [
      talk_sessions[0] == 1,  # Ben should give first talk of whats changed in Parsl this year
      OnDay(talk_sessions[1], 1),  # andrew can only do day 1
      OnDay(talk_sessions[5], 1),  # kevin can only do day 1
      talk_sessions[10] <= talk_sessions[18], # doug taskvine general should come before colin

      OnDay(talk_sessions[15], 1),  # Akila told Ben: I'd prefer to be scheduled on 26th evening (CDT) since I've a conflict on 27th.
      talk_sessions[15] == 3, # Akila -- actually is a tighter version of the directly above constraint

      talk_sessions[16] == 3, # tz australia
      talk_sessions[17] == 4, # josh should start day 2
      talk_sessions[32] == 4, # tz india
      talk_sessions[33] == 4, # tz europe
      YaduConstraints # Yadu's 2 talks should be on different days.
      ]

      YaduConstraints = Or(And(OnDay(talk_sessions[4], 1), OnDay(talk_sessions[23], 2)),
                           And(OnDay(talk_sessions[4], 2), OnDay(talk_sessions[23], 1)))


This gave a schedule which satisfied all of our hard constraints.

Run this code
=============


.. code-block::

  $ pip install z3-solver
  $ python scheduler.py 

