# TODOs for parslfest 2025
# maybe put in some session constraints on a mix of remote and in person, as there is a lot of remote this time?

from z3 import *

# numbers will be represented as bitvecs with this
# many bits - so user must manually make sure its big enough
# to hold results.
BITFIELD = 4

# how much we care about schedule stickiness
stickiness_factor = 0.01

talk_titles_prefs = \
  [

    # first entry is speaker
    # second entry is the published schedule slot (or None if they have none) so that
    #     the solver can try to not move people from the already published schedule.
    # third entry is session stickiness: put Parsl and Globus Compute staff low so that the
    #     solver prefers to move them around rather than other speakers, but non-zero so that
    #     there is still some preference to keep them in the assigned slot
    #     a lower stickiness means these will be moved in preference to a higher stickiness talk
    # fourth entry is talk title
    # fifth entry is "in person" (true)  or "remote" (false)

    # sheet row 2 
    ("Kyle Chard", 1, 1, ["parslfest-meta"], "Introduction to ParslFest", True),
    ("Ben Clifford", None, 0.1, ["parsl-core"], "HTEX Interchange in 3 languages", False),
    ("James Klassen", None, 1, ["geo/env", "imaging"], "Calculating optimal size of Parsl runs for DEM production", False),
    ("Zhao Zhang", None, 1, ["ml"], "Training Neural Networks with Diamond", False),
    ("Sicheng Zhou", None, 1, ["tooling/infra"], "WRATH: Workflow Resilience Across Task Hierarchies in Task-based Parallel Programming Frameworks", False),
    ("Dave Bunten", None, 1, ["bio"], "With Great Parsl Comes Great Portability: Using Parsl through CytoTable for Harmonizing Single-cell Data", False),
    ("Josh Bryan", None, 0.1, ["gc-core"], "Globus Compute Past and Future", True),
    ("Chris Janidlo", None, 0.1, ["gc-core"], "Globus Compute Serialization Overview", True),
    ("Yadu Babuji", None, 0.1, ["site"], "Parsl scaling on Aurora", True),
    ("Laura Walitzer", None, 1, ["simulations"], "A Multifidelity, Multiobjective Optimization Workflow With Parsl", False),
    ("Dan Dietz", None, 1, ["site"], "Globus Compute at OLCF", True),
    ("Tianle Wang", None, 1, ["tooling/infra"], "Integration of globus compute and harvester for ATLAS workflow at HPC", True),
    ("Patrick Wells", None, 1, [], "", True),
    ("Sou Cheng Choi", None, 1, ["simulations"], "Using Parsl for Speeding up QMCPy", False),
    ("João Gabriel Loureiro de Lima Lembo", None, 1, ["tooling/infra"], "Implementing Cold-Start Reduction Techniques on Globus Compute", False),
    ("Chris Harrop", None, 1, ["tooling/infra"], "Enhancements for Parsl and Globus Compute Integration", True),
    ("Haochen Pan", None, 1, ["tooling/infra"], "Globus MCPs for Science and High Performance Computing", True),
    ("Alok Kamatar", None, 1, ["geo/env"], "Core Hours and Carbon: The Environmental Impact of Federated Computing", True),
    ("Hai Duc Nguyen", None, 1, ["imaging", "tomography"], "Resilient Solutions for Tomographic Reconstruction", True),
    ("Daniel Babnigg", None, 1, ["imaging", "astronomy"], "Parallel Scripting in a Integral Field Unit Spectroscopy Pipeline", True),
    ("Geoffrey Lentner", None, 1, ["site"], "Enabling Science for NSF ACCESS via Globus Compute", True),
    ("Pedro Enrique Martinez Fernandez", None, 1, ["provenance/repro"], "Globus Compute + DataLad: Provenance tracking for remote workflows", False),
    ("Douglas N Friedel", None, 0.1, ["tooling/infra", "multisite"], "KeepItRunning: A New Tool for Migrating Running Jobs Between HPC Resources", True),
    ("Will Engler", None, 1, ["ml", "tooling/infra"], "Garden: Lessons learned from serving AI for Science models with Globus Compute", True),
    ("Greg Pauloski", None, 1, ["tooling/infra"], "Academy", False),
    ("Mike Tynes", None, 1, ["materials", "simulations", "ml"], "Distributed on-the-fly training of neural network potentials with Parsl and Colmena", True),
    ("Matt Baughman", None, 1, ["tooling/infra", "multisite"], "Adaptive Task Management: Enabling Multi-Site Workflows with Globus Compute", False),
    ("Valerie Hayot-Sasson", None, 1, ["provenance/repro"], "Facilitating Reproducibility Evaluations on HPC with Globus Compute and GitHub Actions", False),
    ("Arham Khan", None, 1, [], "LSHBloom: Memory-efficient, Extreme-scale Document Deduplication", True),
    ("Mansi Sakarvadia", None, 1, ["ml"], "Topology-Aware Knowledge Propagation in Decentralized Learning", False),
    ("Logan Ward", None, 0.1, ["materials", "ml", "simulations"], "Deploying AI+Simulation Workflows for MOF Design (with Parsl)", False),
    ("Kelechi Annabelle Nwankwo", None, 1, ["tooling/infra"], "Parslet: Making Workflow Automation Accessible on Android and Low-Power Devices", False),
    ("Stefan Gary", None, 1, [], "Using parsl-perf to evaluate performance in a hybrid HPC environment", False),
  ]


talk_sessions = [BitVec(f'talk_{n}_in_session', BITFIELD) for n in range(0,len(talk_titles_prefs))]

# two different session structures: 2 bigger sessions, or 3 smaller sessions, per day
# session_sizes = [7,8,0,7,7,0]
session_sizes = [6,6,6,6,6,6]
n_sessions = len(session_sizes)

assert sum(session_sizes) >= len(talk_titles_prefs), "must be enough slots for each talk"

# each talk must be in a valid session
talks_in_valid_sessions = [And(t >= 1, t <= n_sessions) for t in talk_sessions]

# session capacities

def SessionSize(session, size):
    return AtMost(*[t == session for t in talk_sessions], size)


sessions_have_sizes = [SessionSize(n+1, session_sizes[n]) for n in range(0,len(session_sizes))]

def OnDay(talk_session, day):
  if day == 1:
    return And(talk_session >= 1, talk_session <= 3)
  elif day == 2:
    return And(talk_session >= 4, talk_session <= 6)
  else:
    raise RuntimeError("bad day")

# YaduConstraints = Or(And(OnDay(talk_sessions[4], 1), OnDay(talk_sessions[23], 2)),
#                      And(OnDay(talk_sessions[4], 2), OnDay(talk_sessions[23], 1)))
  

special_talk_constraints = [
   talk_sessions[0] == 1, # Kyle must talk first
   OnDay(talk_sessions[6], 1),  # Josh can only do day 1 in person
   talk_sessions[6] != talk_sessions[0], # GC intro should not be in same session as Parsl into 
   talk_sessions[6] <= talk_sessions[7], # GC intro should come before other GC talks
   talk_sessions[1] >= 3,  # Ben doesn't want to talk in first two sessions
   ]

#  OnDay(talk_sessions[1], 1),  # andrew can only do day 1
#  OnDay(talk_sessions[5], 1),  # kevin can only do day 1
#  talk_sessions[10] <= talk_sessions[18], # doug taskvine general should come before colin

#  OnDay(talk_sessions[15], 1),  # Akila told Ben: I'd prefer to be scheduled on 26th evening (CDT) since I've a conflict on 27th.
#  talk_sessions[15] == 3, # Akila -- actually is a tighter version of the directly above constraint

#  talk_sessions[16] == 3, # tz australia
#  talk_sessions[17] == 4, # josh should start day 2
#  talk_sessions[32] == 4, # tz india
#  talk_sessions[33] == 4, # tz europe
#  YaduConstraints # Yadu's 2 talks should be on different days.
#  ]


possible_session_chairs = [
  "Dan Katz",  #0
  "Chris Janidlo", #1
  "Yadu Babuji", #2
  "Kyle Chard", #3
  "ADDITIONAL CHAIR #4", #4
  "ADDITIONAL CHAIR #6", #5
  ]

# sticky_session_chairs = [2, 0, 5, 4, 3, 1]
sticky_session_chairs = [None, None, None, None, None, None]

session_chairs = [BitVec(f'session_{n}_has_chair', BITFIELD) for n in range(0,n_sessions)]

session_chairs_are_valid = [And(sc >= 0, sc < len(possible_session_chairs)) for sc in session_chairs]

# check that someone does not chair two sessions

def ChairHasMaxOneSession(chairnum):
  return AtMost(*[sc == chairnum for sc in session_chairs], 1)

chairs_maximum_one_session = And(*[ChairHasMaxOneSession(n) for n in range(0, len(possible_session_chairs))])

# exclude speakers from chairing their own session

def ChairTalkExclusion(talk, chairnum):
  return And(*[Not(And(talk_sessions[talk] == session+1, session_chairs[session] == chairnum)) for session in range(0, n_sessions)])

special_chair_constraints = [
  session_chairs[0] != 1,  # Chris first time chair, so make two sessions happen before he chairs to get vibe
  session_chairs[1] != 1,  # "
  ]

for sc_n in range(0, len(possible_session_chairs)):
  print(f"Excluding talks for possibel session chair {sc_n} -- {possible_session_chairs[sc_n]}")
  for ses_n in range(0, len(talk_titles_prefs)):
    if talk_titles_prefs[ses_n][0] == possible_session_chairs[sc_n]:
      print(f"Excluding speaker for talk {ses_n}")
      special_chair_constraints.append(ChairTalkExclusion(ses_n, sc_n))


#   ChairTalkExclusion(0, 1),   # talk 0 cannot be in session chaired by chair 1 -- that's Ben

#   ChairTalkExclusion(24, 0),  # Dan

#   ChairTalkExclusion(5, 2),   # Kevin
#   session_chairs[3] != 2, # Kevin cannot chair on any day2 session
#   session_chairs[4] != 2,  # Kevin cannot chair on any day2 session
#   session_chairs[5] != 2,  # Kevin cannot chair on any day2 session

#   ChairTalkExclusion(4, 3),   # Yadu
#   ChairTalkExclusion(23, 3),   # Yadu

#   session_chairs[0] != 4, # Kyle (doesn't have a talk in the sense of this scheduler, but is doing intro)

#   ChairTalkExclusion(30, 5)   # Reid
# ]

num_moved = Sum(*[If(talk_sessions[n] == talk_titles_prefs[n][1], 0, talk_titles_prefs[n][2] if len(talk_titles_prefs[n]) > 2 else 1) for n in range(0,len(talk_titles_prefs)) if talk_titles_prefs[n][1] is not None])

topics = set()
for talk in talk_titles_prefs:
  assert isinstance(talk[3], list)
  topics.update(talk[3])

print(f"Topics: {topics}")
topics_deterministic = sorted(list(topics))

print(f"Topics deteministic: {topics}")

objective_function = stickiness_factor * num_moved

s = Optimize()
s.add(talks_in_valid_sessions)
s.add(sessions_have_sizes)
s.add(special_talk_constraints)

s.add(session_chairs_are_valid)
s.add(chairs_maximum_one_session)
s.add(special_chair_constraints)

# constraint based topics

for topic in topics_deterministic:
  talks_in_topic = [talk_sessions[n] for n in range(0, len(talk_titles_prefs)) if topic in talk_titles_prefs[n][3]]

  if len(talks_in_topic) > 1:

    # so that we will get a soft score of 1 if all the soft constraints for this topic are satisfied
    talk_constraint_strength = 1.0 / (len(talks_in_topic) * (len(talks_in_topic) - 1))

    print(f"Topic {topic} has {len(talks_in_topic)} talks. Soft constraint score is {talk_constraint_strength}")


    for a in talks_in_topic:
      for b in talks_in_topic:
        # these tests should massively reduce the number of soft constraints on large topic groups
        # in practice on parslfest 2025, this reduce solving from 15 minute to 5 seconds
        if a is b:
          print("skipping self-pairing")
        elif id(a) > id(b):  # arbitrary ordering
          print("skipping mirror pairing")
        else:
          print(f"Adding a topic affinity for {a} and {b}")
          s.add_soft(a == b, weight=talk_constraint_strength)

# if you're getting errors here about objective function being a float,
# (and of value 0), it's because there aren't any stickiness pairs to
# evaluate - because nothing is pinned. Pin a single talk (eg the
# intro) by hand.
s.minimize(objective_function)

# session chairs are sticky
for n in range(n_sessions):
  if sticky_session_chairs[n] is not None:
    s.add_soft(session_chairs[n] == sticky_session_chairs[n], weight="0.1")

print("solving")
result = s.check()

print(result)

if result == unsat :
    print(s.unsat_core())
    raise RuntimeError("Cannot schedule ParslFest 2024 :(")

m=s.model()
print(m)
print("objectives:")
print(s.objectives())
print("sexpr:")
print(s.sexpr())
print("stats:")
print(s.statistics())
print("\n\nformatted:")


for session in range(1, n_sessions+1):
  chairname = possible_session_chairs[m.evaluate(session_chairs[session - 1]).as_long()]
  print(f"\nSession {session} - chair {chairname}")
  used = 0
  for n in range(0, len(talk_titles_prefs)):
    if m.evaluate(talk_sessions[n]) == session:
      # if talk_titles_prefs[n][1] is None:
      #  print("**NEW** ", end='')
      # elif session != talk_titles_prefs[n][1]:
      #  print("**MOVED** ", end='')
      print(talk_titles_prefs[n][0], end='')
      print(" - ", end='')
      print(talk_titles_prefs[n][4], end='  ')
      if talk_titles_prefs[n][5]:
        print("(in person)", end=' ')
      else:
        print("(remote)", end=' ')
      print(talk_titles_prefs[n][3])
      used += 1
  for _ in range(0, session_sizes[session-1] - used):
    print("**SPARE SLOT**")
  if used > session_sizes[session-1]:
    print("**ERROR** too many talks assigned to this session")
