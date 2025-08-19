# TODOs for parslfest 2025
# maybe put in some session constraints on a mix of remote and in person, as there is a lot of remote this time?

from z3 import *

# numbers will be represented as bitvecs with this
# many bits - so user must manually make sure its big enough
# to hold results.
BITFIELD = 4

# how much we care about schedule stickiness
stickiness_factor = True

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
    # ("Kyle Chard", 1, 1, ["parslfest-meta"], "Introduction to ParslFest", True),

    #0 
    ("Ben Clifford", None, 0.1, ["pl"], "HTEX Interchange in 3 languages", False),
    ("James Klassen", 4, 1, ["geo/env", "imaging"], "Calculating optimal size of Parsl runs for DEM production", False),
    ("Zhao Zhang", 2, 1, ["ml"], "Training Neural Networks with Diamond", False),
    ("Sicheng Zhou", 1, 1, ["tooling/infra"], "WRATH: Workflow Resilience Across Task Hierarchies in Task-based Parallel Programming Frameworks", False),
    ("Dave Bunten", 6, 1, ["bio"], "With Great Parsl Comes Great Portability: Using Parsl through CytoTable for Harmonizing Single-cell Data", False),
    ("Josh Bryan", 3, 0.1, ["gc-core"], "Globus Compute Past and Future", True),
    ("Chris Janidlo", 3, 0.1, ["gc-core"], "Globus Compute Serialization Overview", True),
    ("Yadu Babuji", 6, 0.1, ["site"], "Parsl scaling on Aurora", True),
    ("Laura Walitzer", 2, 1, ["simulations"], "A Multifidelity, Multiobjective Optimization Workflow With Parsl", False),
    ("Dan Dietz", 6, 1, ["site"], "Globus Compute at OLCF", True),

    #10 
    ("Tianle Wang", 5, 1, ["tooling/infra"], "Integration of globus compute and harvester for ATLAS workflow at HPC", True),
    ("Patrick Wells", 4, 1, ["space"], "OpenCosmo", True),
    ("João Gabriel Loureiro de Lima Lembo", 1, 1, ["tooling/infra"], "Implementing Cold-Start Reduction Techniques on Globus Compute", False),
    ("Chris Harrop", 1, 1, ["tooling/infra"], "Enhancements for Parsl and Globus Compute Integration", True),
    ("Haochen Pan", 5, 1, ["tooling/infra"], "Globus MCPs for Science and High Performance Computing", True),
    ("Alok Kamatar", 4, 1, ["geo/env"], "Core Hours and Carbon: The Environmental Impact of Federated Computing", True),
    ("Hai Duc Nguyen", 1, 1, ["imaging", "tomography"], "Resilient Solutions for Tomographic Reconstruction", True),
    ("Daniel Babnigg", 4, 1, ["imaging", "space"], "Parallel Scripting in a Integral Field Unit Spectroscopy Pipeline", True),
    ("Geoffrey Lentner", 6, 1, ["site"], "Enabling Science for NSF ACCESS via Globus Compute", True),
    ("Pedro Enrique Martinez Fernandez", 3, 1, ["provenance/repro"], "Globus Compute + DataLad: Provenance tracking for remote workflows", False),

    #20
    ("Douglas N Friedel", 5, 0.1, ["tooling/infra", "multisite"], "KeepItRunning: A New Tool for Migrating Running Jobs Between HPC Resources", True),
    ("Will Engler", 2, 1, ["ml", "tooling/infra"], "Garden: Lessons learned from serving AI for Science models with Globus Compute", True),
    ("Greg Pauloski", 5, 1, ["academy"], "Academy", False),
    ("Mike Tynes", 2, 1, ["materials", "simulations", "ml"], "Distributed on-the-fly training of neural network potentials with Parsl and Colmena", True),
    ("Matt Baughman", None, 1, ["tooling/infra", "multisite"], "Adaptive Task Management: Enabling Multi-Site Workflows with Globus Compute", True),
    # ^ on programme as session 2
    ("Valerie Hayot-Sasson", 3, 1, ["provenance/repro"], "Facilitating Reproducibility Evaluations on HPC with Globus Compute and GitHub Actions", False),
    ("Arham Khan", 3, 1, [], "LSHBloom: Memory-efficient, Extreme-scale Document Deduplication", True),
    ("Mansi Sakarvadia", 4, 1, ["ml"], "Topology-Aware Knowledge Propagation in Decentralized Learning", False),
    ("Logan Ward", 2, 0.1, ["materials", "ml", "simulations"], "Deploying AI+Simulation Workflows for MOF Design (with Parsl)", False),
    ("Kelechi Annabelle Nwankwo", 1, 1, ["tooling/infra"], "Parslet: Making Workflow Automation Accessible on Android and Low-Power Devices", False),

    #30
    ("Stefan Gary", 5, 1, ["tooling/infra", "multisite"], "Using parsl-perf to evaluate performance in a hybrid HPC environment", False),
    ("Ben Clifford", None, 0.1, ["monitoring"], "Parsl monitoring message flows", False),
    ("Robert Underwood", 2, 1, ["ml"], "Using Parsl to Power the Data Pipelines of AuroraGPT", False),
    ("Scott Friedman", 1, 1, ["tooling/infra"], "An ephemeral Parsl provider for AWS", False),
    ("Seena Vazifedunn", 1, 1, ["tooling/infra"], "StreamHub: High-performance Managed SciStream as a Service", True),
    ("Naomi Kolodisner", 6, 1, ["academy"], "Adaptive Tool Selection in a Scalable Genomics Pipeline", False),
    ("Joshua Herman", 3, 1, ["montecarlo"], "Accelerating QMCPy Notebook Tests with Parsl", False),
    ("Alex Brace", 5, 1, [""], "precorded video", False),
  ]


talk_sessions = [BitVec(f'talk_{n}_in_session', BITFIELD) for n in range(0,len(talk_titles_prefs))]

# two different session structures: 2 bigger sessions, or 3 smaller sessions, per day
# session_sizes = [9,9,9,9]
session_sizes = [7,7,6,6,6,6]
n_sessions = len(session_sizes)

assert sum(session_sizes) >= len(talk_titles_prefs), "must be enough slots for each talk"

ipt =  len([t for t in talk_titles_prefs if t[5]])
ipf = ipt / len(talk_titles_prefs)
print(f"Fraction of talks that are in-person: {ipt} / {len(talk_titles_prefs)} = {ipf}")
# assert len([t for t in talk_titles_prefs if t[5]]) * 2 >= len(talk_titles_prefs), "must be at least 50% in person to satisfy remote spread count"


# each talk must be in a valid session
talks_in_valid_sessions = [And(t >= 1, t <= n_sessions) for t in talk_sessions]

# session capacities

def SessionSize(session, size):
    if size == 0:
     sp = 0
    else:
     sp = size - 1
    return And(AtMost(*[t == session for t in talk_sessions], size),
               AtLeast(*[t == session for t in talk_sessions], 6),  # don't want sessions to be rounded down if they are shorter sessions... the longest sessions are the ones that can flex
              )

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
  
## num_moved = Sum(*[If(talk_sessions[n] == talk_titles_prefs[n][1], 0, talk_titles_prefs[n][2] if len(talk_titles_prefs[n]) > 2 else 1) for n in range(0,len(talk_titles_prefs)) if talk_titles_prefs[n][1] is not None])
special_talk_constraints = [
   # talk_sessions[0] == 1, # Kyle must talk first
   OnDay(talk_sessions[5], 1),  # Josh can only do day 1 in person
   # talk_sessions[5] != talk_sessions[0], # GC intro should not be in same session as Parsl intro 
   talk_sessions[5] <= talk_sessions[6], # GC intro should come before other GC talks

   # these are deliberately different, due to content
   talk_sessions[0] > 3,  # 3-languages talk should be on day 2
   talk_sessions[31] !=  3, # Ben doesn't want to talk in TZ inconvenient times about monitoring
   talk_sessions[0] > talk_sessions[31],  # ben's two talks should be in different sessions, and talk 31, being more serious, should come earlier?

   talk_sessions[35] >= talk_sessions[22],  # academy app talk should be after greg's main academy talk
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
  "Yadu Babuji", #3
  "Kyle Chard", #4
  "Kyle Chard", #5
  ]

# session numbers here start at 0, not 1
# sticky_session_chairs = [None, None, None, None, None, None]
sticky_session_chairs = [0, 2, 4, 3, 1, 5]

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

num_moved = Sum(*[If(talk_sessions[n] == talk_titles_prefs[n][1], 0, 1) for n in range(0,len(talk_titles_prefs)) if talk_titles_prefs[n][1] is not None])

topics = set()
for talk in talk_titles_prefs:
  assert isinstance(talk[3], list)
  topics.update(talk[3])

print(f"Topics: {topics}")
topics_deterministic = sorted(list(topics))

print(f"Topics deteministic: {topics}")


s = Optimize()
s.add(talks_in_valid_sessions)
s.add(sessions_have_sizes)
s.add(special_talk_constraints)

s.add(session_chairs_are_valid)
s.add(chairs_maximum_one_session)
s.add(special_chair_constraints)

if stickiness_factor:
  objective_function = num_moved
  s.minimize(objective_function)

for session in range(1, n_sessions+1):
  num_in_session = Sum(*[If(talk_sessions[n] == session, 1, 0) for n in range(0, len(talk_titles_prefs))])
  num_in_person = Sum(*[If(talk_sessions[n] == session, 1, 0) for n in range(0, len(talk_titles_prefs)) if talk_titles_prefs[n][5]])
  # num_remote = Sum(*[If(talk_sessions[n] == session, 1, 0) for n in range(0, len(talk_titles_prefs)) if not talk_titles_prefs[n][5]])
  # condition = num_in_person >= num_remote
  # s.add_soft(condition)   # can't be hard because we don't have enough in-person talks at time of writing

  # these numbers are hard-coded from looking at the session sizes and ratios. the hard constraint is to try to speed up optimisation
  # and to give a hard minimum on the number of in-person talks in a session.
  # and the soft constraint is to reward when a session goes beyond the minimum that can be achieved for every session.

  # for 6 sessions - this can probably be computed as the lower and upper bounds of the fraction of talks that are in person
  # compared to the expected slot size, or something like that. or something more complicated for the particular slot based
  # on how many sessions are assigned to that actual slot - so that a 6 entry session always gets 3, but a 5 entry session can have 2?
  s.add_soft(Or( And(num_in_person >= 2, num_in_person <=3, num_in_session == 5),
            And(num_in_person >= 2, num_in_person <=3, num_in_session == 6),
            And(num_in_person >= 3, num_in_person <=4, num_in_session == 7)
          ),
          id='session_ratio'
       )

  # for 4 sessions
  # s.add(num_in_person >= 4)
  # s.add(num_in_person <= 5)

# constraint based topics

for topic in topics_deterministic:
  talks_in_topic = [talk_sessions[n] for n in range(0, len(talk_titles_prefs)) if topic in talk_titles_prefs[n][3]]

  if len(talks_in_topic) > 1:

    # so that we will get a soft score of 1 if all the soft constraints for this topic are satisfied
    # but we can never have more than the largest size of a session clustered together
    # so max out there - so that 2 max-sized session clusters will score 2 points.

    max_topic_cluster = min(len(talks_in_topic), max(session_sizes))
    print(f"Topic {topic} has max cluster size {max_topic_cluster}")
    # talk_constraint_strength = 1.0 / (len(talks_in_topic) * (len(talks_in_topic) - 1))
    talk_constraint_strength = 1.0 / (max_topic_cluster * (max_topic_cluster - 1))

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
      if talk_titles_prefs[n][1] is None:
        print("**NEW** ", end='')
      elif session != talk_titles_prefs[n][1]:
        print("**MOVED** ", end='')
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
