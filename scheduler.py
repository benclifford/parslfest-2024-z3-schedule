from z3 import *

# numbers will be represented as bitvecs with this
# many bits - so user must manually make sure its big enough
# to hold results.
BITFIELD = 4

# how much we care about schedule stickiness
stickiness_factor = 0.01

talk_titles_prefs = \
  [

    # first entry is talk title
    # second entry is the published schedule slot (or None if they have none) so that
    #     the solver can try to not move people from the already published schedule.
    # third entry is session stickiness: put Parsl and Globus Compute staff low so that the
    #     solver prefers to move them around rather than other speakers, but non-zero so that
    #     there is still some preference to keep them in the assigned slot
    #     a lower stickiness means these will be moved in preference to a higher stickiness talk

    #0 
    ("Ben Clifford: A Year in Parsl Development", 1, 0.1, ["parsl-core"]),
    ("Andrew S. Rosen: The Quantum Accelerator: Accessible and Scalable Materials Science Workflows", 1, 1, ["chem"]),
    ("Sander Vandenhaute: Scalable Molecular Simulation", 1, 1, ["chem"]),
    ("Douglas N. Friedel: Tracking File Provenance with Parsl", 3, 0.1, ["provenance"]),
    ("Yadu Babuji: MPI+FaaS: Extending Parsl and Globus Compute to Represent and Execute MPI Tasks", 6, 0.1, ["parslgc"]),

    #5
    ("Kevin Hunter Kesling: Globus Compute Update", 3, 0.1, ["gc-core"]),
    ("Christopher Harrop: Federated Numerical Weather Prediction Workflows with MPAS", 2, 1, ["earth"]),
    ("Mansi Sakarvadia: Scaling ML Interpretability Experiments Using Parsl", 5, 1, ["ai/ml"]),
    ("Michael Buehlmann: Analysis Portal for Cosmological Simulations", 2, 1, ["portal"]),
    ("Takuya Kurihana: Scalable earth observation ML workflow in climate applications", 5, 1, ["earth", "ai/ml"]),
    ("Douglas Thain: TaskVine Overview", 2, 1, ["taskvine"]),

    #11
    ("Christine Simpson: Parsl at ALCF: Use cases and challenges for IRI, Aurora, and beyond", 6, 1, ["infrastructure"]),
    ("Zilinghan Li and Ravi K. Madduri: Using Globus Compute to Streamline Federated Learning Applications", 5, 1, ["ai/ml"]),
    ("Matthew Baughman: Task Orchestration in Heterogeneous Computing Environments using Globus Compute", 6, 1, ["infrastructure"]),
    ("Nitin Ranjan: Application of AI analytics to Taxation", 5, 1, ["ai/ml"]),
    ("Akila Ravihansa Perera: Enabling Economical and Scalable Genomic Workflows", 3, 1, ["bio"]),
    ("Gus Ellerm: Extending Globus Compute with RO-Crate provenance models", 3, 1, ["provenance"]),

    #17
    ("Josh A. Bryan: Future of Globus Compute", 4, 0.1, ["gc-core"]),
    ("Colin Thomas: Parsl and TaskVine: Interactions Between DAG Managers and Workflow Executors", 2, 1, ["taskvine"]),
    ("Andre Bauer: The Globus Compute Dataset: An Open Function-as-a-Service Dataset From the Edge to the Cloud", 4, 1, ["gc-core"]),
    ("Rajat Bhattarai: Dynamic Resource Management for Elastic Scientific Workflows", 6, 1, ["infrastructure"]),
    ("Inna Brodkin: Extreme-Scale Monitoring of Parsl Workflows with Chronolog", 6, 1, ["infrastructure"]),
    ("Hemant Sharma: Parsl and Globus Compute for a Hybrid Workflow", 3, 1, ["parslgc"]),
    ("Yadu Babuji: Replacing Channels with Globus Compute Executors in Parsl", 3, 0.1, ["parslgc"]),

    #24
    ("Daniel S. Katz: An Update on Parsl Sustainability", 1, 0.1, ["parsl-core"]),
    ("Valerie Hayot-Sasson: Developing Distributed High-performance Computing Capabilities of an Open Science Platform for Robust Epidemic Analysis", 4, 1, ["bio"]),
    ("Arha Gautram: Decorators and Function Parameters", 1, 1, ["parsl-core"]),
    ("Tyler J. Skluzacek: A Workflows Ecosystem for ESGF Data", 2, 1, ["earth"]),
    ("Nischay Karle: Usage Tracking Stats of Parsl", 1, 1, ["parsl-core"]),
    ("Lola Obielodan: Synergies among Parsl, MLOPs, and custom cloud clusters", 5, 1, ["ai/ml"]),
    ("Reid Mello: Multi-user Globus Compute endpoints", 4, 0.1, ["gc-core"]),

    #31
    ("Haotian Xie (Rutgers University): TBD – talk about Diamond, an integration portal that allows users to easily use globus-compute via a frontend.", 2, 1, ["portal"]),
    ("Divyansh Goyal (Guru Gobind Singh Indraprastha University): Parallel scripting in medical imaging", 4, 1, ["bio"]),
    ("Dante D. Sanchez-Gallegos (University Carlos III of Madrid): Creating Wide-Area Distribution Systems with DynoStore and Globus Compute", 4, 1, ["infrastructure"]),
    ("Satyarth Praveen: Leveraging Globus API for High-Performance Data Transfer and Computation", 1, 1, []),
    ("Greg Pauloski: TaPS: A Performance Evaluation Suite for Task-based Execution Frameworks ", 6, 1, ["infrastructure"])
  ]


talk_sessions = [BitVec(f'talk_{n}_in_session', BITFIELD) for n in range(0,len(talk_titles_prefs))]

n_sessions = 6

# each talk must be in a valid session
talks_in_valid_sessions = [And(t >= 1, t <= n_sessions) for t in talk_sessions]

# session capacities

def SessionSize(session, size):
    return AtMost(*[t == session for t in talk_sessions], size)

session_sizes = [7,6,6,6,5,6]

sessions_have_sizes = [SessionSize(n+1, session_sizes[n]) for n in range(0,len(session_sizes))]

def OnDay(talk_session, day):
  if day == 1:
    return And(talk_session >= 1, talk_session <= 3)
  elif day == 2:
    return And(talk_session >= 4, talk_session <= 6)
  else:
    raise RuntimeError("bad day")

YaduConstraints = Or(And(OnDay(talk_sessions[4], 1), OnDay(talk_sessions[23], 2)),
                     And(OnDay(talk_sessions[4], 2), OnDay(talk_sessions[23], 1)))
  

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


possible_session_chairs = [
  "Dan Katz",  #0
  "Ben Clifford", #1
  "Kevin Hunter Kesling", #2
  "Yadu Babuji", #3
  "Kyle Chard", #4
  "Reid Mello" #5
  ]

sticky_session_chairs = [2, 0, 5, 4, 3, 1]

session_chairs = [BitVec(f'session_{n}_has_chair', BITFIELD) for n in range(0,n_sessions)]

session_chairs_are_valid = [And(sc >= 0, sc < len(possible_session_chairs)) for sc in session_chairs]

# check that someone does not chair two sessions

def ChairHasMaxOneSession(chairnum):
  return AtMost(*[sc == chairnum for sc in session_chairs], 1)

chairs_maximum_one_session = And(*[ChairHasMaxOneSession(n) for n in range(0, len(possible_session_chairs))])

def ChairTalkExclusion(talk, chairnum):
  return And(*[Not(And(talk_sessions[talk] == session+1, session_chairs[session] == chairnum)) for session in range(0, n_sessions)])

special_chair_constraints = [
   ChairTalkExclusion(0, 1),   # talk 0 cannot be in session chaired by chair 1 -- that's Ben

   ChairTalkExclusion(24, 0),  # Dan

   ChairTalkExclusion(5, 2),   # Kevin
   session_chairs[3] != 2, # Kevin cannot chair on any day2 session
   session_chairs[4] != 2,  # Kevin cannot chair on any day2 session
   session_chairs[5] != 2,  # Kevin cannot chair on any day2 session

   ChairTalkExclusion(4, 3),   # Yadu
   ChairTalkExclusion(23, 3),   # Yadu

   session_chairs[0] != 4, # Kyle (doesn't have a talk in the sense of this scheduler, but is doing intro)

   ChairTalkExclusion(30, 5)   # Reid
 ]

num_moved = Sum(*[If(talk_sessions[n] == talk_titles_prefs[n][1], 0, talk_titles_prefs[n][2] if len(talk_titles_prefs[n]) > 2 else 1) for n in range(0,len(talk_titles_prefs)) if talk_titles_prefs[n][1] is not None])

topics = set()
for talk in talk_titles_prefs:
  topics.update(talk[3])

topics_deterministic = sorted(list(topics))


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
  for a in talks_in_topic:
    for b in talks_in_topic:
      s.add_soft(a == b)

s.minimize(objective_function)

# session chairs are sticky
for n in range(n_sessions):
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
      print(talk_titles_prefs[n][0], end='   ')
      print(talk_titles_prefs[n][3])
      used += 1
  for _ in range(0, session_sizes[session-1] - used):
    print("**SPARE SLOT**")
  if used > session_sizes[session-1]:
    print("**ERROR** too many talks assigned to this session")
