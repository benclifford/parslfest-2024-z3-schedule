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

Session structure
-----------------

The first constraints I added are to do with the structure of the sessions, rather than the constraints I talked about in the introduction:

* each talk must be in a valid session: for example, a talk cannot be scheduled in session 99.

  This was implemented by declaring this constraint 35 times (one for each talk):

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

Talk constraints
----------------

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


This gave a schedule which satisfied all of our hard constraints, and as an advantage to the manual approach, allowed further experimentation while preserving all the constraints. This is maybe the point that this code became "better" than the manual approach. Although I was the only one editing constraints, it would have been possible for someone else to have pushed other constraints into the code, like any other code modification, and there was a GitHub-visible list of constraints so that others could check if a particular constraint was specified, even if they weren't editing the constraints.

Grouping by topics
------------------

Next, I wanted to see what theme based grouping I could make work here. I assigned each talk a list of topic keywords based on what I knew about each talk: the talk title and in some cases personal knowledge of the speaker's work. I tried a couple of ways of implementing grouping. My first implementation (introduced in `this commit <https://github.com/benclifford/parslfest-2024-z3-schedule/commit/6746bb0f296bf6bc750d9e0326e3627c100bfb00#diff-e875a684611661e9011e4e179a1c6c2c398a3bd2148862694388a87e7b3a55e3R150>`_ and subsequently removed) was quite maths-heavy and slow to solve). I replaced that with a soft constraint based implementation which solves much faster. For every topic, every pair of talks that shares that topic gets a soft constraint to be in the same session.

.. code-block::

  for topic in topics_deterministic:
    talks_in_topic = [talk_sessions[n] for n in range(0, len(talk_titles_prefs)) if topic in talk_titles_prefs[n][3]]
    for a in talks_in_topic:
      for b in talks_in_topic:
        s.add_soft(a == b)

I don't really have a feel for how well this works in general, but for the ParslFest programme it produced some acceptable groupings: All ``ai/ml`` talks ended up in session 5, and that session was only ``ai/ml`` talks. Session 6 was mostly ``infrastructure`` talks, and other sessions contained groups of smaller topic tags. The most varied session was session 3, caused primarily by timezone constraints forcing a few speakers here that could not bring their whole topic group with them.

In the end we didn't label the sessions with topics but I guess I could have done this semi-automatically. The generated programme output listed the topic tags for each talk so at themes are visible by eye.


Stickiness
----------

My colleague Sophie replaced the online programme with the output of this code the day after I implemented topic grouping above. After that, I wanted the code to keep session assignments if possible, only changing people to different slots if this led to better grouping. Otherwise, it was possible that changing constraints would generate a completely different but equally satisfactory programme.

So I implemented session stickiness. I added a published session value to every talk, which was a manual record of which session the talk had been published to be in. Then for every talk I added a soft constraint that that talk should be placed in that session. This would not stop rearrangements if it led to a better programme, but would otherwise nudge the programme towards staying the same.

I implemented this with objective functions rather than ``add_soft`` constraints, because at the time of implementation I had learned about objective functions and not about ``add_soft``. 

Generally, for each talk that was moved, the schedule got 1 penalty point. But I also implemented a friendly-speakers option: each talk was annotated with a movement penalty score. This let me specify that some speakers (generally people on the core teams who I knew personally) should be moved in preference to others.

If I implemented this again, i would have used ``add_soft`` - and in the chair handling code that's what I did.


Session chairs
--------------

Each session has a chair, to keep order and pace.

These have also been allocated manually in previous years, extremely informally.

As it is usually me allocating the session chairs manually and I was in the flow, I added that here too.

I put in a list of (around 6) available chairs, who were all also speakers.

For each session, I declared a variable identifying the chair. This relation is the other way round to talks having a session: talks have one identified session, but sessions have one identified chair.

Then I added constraints for:

* basic structure: a session must be chaired by a valid chair (a valid chair number)

* chair availability: like with the talks, some people were only available on some days. (abstracting back a level, this is availability on a human, rather than on a talk or a chair, and maybe it would be interesting to describe availability relations with that abstraction, once... but here there were sufficiently few constraints I did not do so)

* chairs should not speak in a session they chair. This was implemented as a manual list of which chairs had which numbered talks.

* chairs should chair at most 1 session (although they might not be used as a chair at all: unlike talks, there is no requirement to schedule all possible chairs)

* chair assignment should be sticky - like sticky talk sessions, but using ``add_soft``

None of this chair scheduling was complicated compared to the earlier parts.

Would I do this again?
----------------------

Yes. We got a better schedule than manual scheduling, because we got talk grouping, something people have asked for; we got more confidence about our hard constraints; and we were easily able to reschedule after a "major event" within minutes: adding so many more talks that we wanted to restructure two sessions into three.

Most of the time (a very long evening) was spent learning Z3 and techniques for scheduling. This README is in part for when I want to do this again, so I don't have to re-learn. (hello, me in 2025!)

Even More Overengineering
-------------------------

* break placement: there was some flexibility on how many talks were in each session (for example, fairly regularly spaced breaks but we could have moved them slightly to accomodate talk grouping)

* what different ways are available for grouping talks? I feel like the current talk grouping will do things like double the affinity of talks that share two keywords, which I don't think I want to happen.

Run this code
=============


.. code-block::

  $ pip install z3-solver
  $ python scheduler.py 

