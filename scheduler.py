from z3 import *

talk_titles_prefs = \
  [

    # first entry is talk title
    # second entry is the published schedule slot (or None if they have none) so that
    #     the solver can try to not move people from the already published schedule.
    # third entry is moveability-prefence: put Parsl and Globus Compute staff low so that the
    #     solver prefers to move them around rather than other speakers, but non-zero so that
    #     there is still some preference to keep them in the assigned slot
    #0 
    ("Ben Clifford: A Year in Parsl Development", 1, 0.1),
    ("Andrew S. Rosen: The Quantum Accelerator: Accessible and Scalable Materials Science Workflows", 1),
    ("Sander Vandenhaute: Scalable Molecular Simulation", 1),
    ("Douglas N. Friedel: Tracking File Provenance with Parsl", 1, 0.1),
    ("Yadu Babuji: MPI+FaaS: Extending Parsl and Globus Compute to Represent and Execute MPI Tasks", 1, 0.1),

    #5
    ("Kevin Hunter Kesling: Globus Compute Update", 2, 0.1),
    ("Christopher Harrop: Federated Numerical Weather Prediction Workflows with MPAS", 2),
    ("Mansi Sakarvadia: Scaling ML Interpretability Experiments Using Parsl", 2),
    ("Michael Buehlmann: Analysis Portal for Cosmological Simulations", 2),
    ("Takuya Kurihana: ", 2),
    ("Douglas Thain: TaskVine Overview", 2),

    #11
    ("Christine Simpson: Parsl at ALCF: Use cases and challenges for IRI, Aurora, and beyond", 3),
    ("Zilinghan Li and Ravi K. Madduri: Using Globus Compute to Streamline Federated Learning Applications", 3),
    ("Matthew Baughman: Task Orchestration in Heterogeneous Computing Environments using Globus Compute", 3),
    ("Nitin Ranjan: Application of AI analytics to Taxation", 3),
    ("Akila Ravihansa Perera: Enabling Economical and Scalable Genomic Workflows", 3),
    ("Gus Ellerm: Extending Globus Compute with RO-Crate provenance models", 3),

    #17
    ("Josh A. Bryan: Future of Globus Compute", 4, 0.1),
    ("Colin Thomas: Parsl and TaskVine: Interactions Between DAG Managers and Workflow Executors", 4),
    ("Andre Bauer: The Globus Compute Dataset: An Open Function-as-a-Service Dataset From the Edge to the Cloud", 4),
    ("Rajat Bhattarai: Dynamic Resource Management for Elastic Scientific Workflows", 4),
    ("Inna Brodkin: Extreme-Scale Monitoring of Parsl Workflows with Chronolog", 4),
    ("Hemant Sharma: Parsl and Globus Compute for a Hybrid Workflow", 4),
    ("Yadu Babuji: Replacing Channels with Globus Compute Executors in Parsl", 4, 0.1),

    #24
    ("Daniel S. Katz: An Update on Parsl Sustainability", 5, 0.1),
    ("Valerie Hayot-Sasson: Developing Distributed High-performance Computing Capabilities of an Open Science Platform for Robust Epidemic Analysis", 5),
    ("Arha Gautram: Decorators and Function Parameters", 5),
    ("Tyler J. Skluzacek: A Workflows Ecosystem for ESGF Data", 5),
    ("Nischay Karle: Usage Tracking Stats of Parsl", 5),
    ("Lola Obielodan: Synergies among Parsl, MLOPs, and custom cloud clusters", 5),
    ("Reid Mello: Multi-user Globus Compute endpoints", 5, 0.1),

    #31
    ("Haotian Xie (Rutgers University): TBD – talk about Diamond, an integration portal that allows users to easily use globus-compute via a frontend.", None),
    ("Divyansh Goyal (Guru Gobind Singh Indraprastha University): Parallel scripting in medical imaging", None),
    ("Dante D. Sanchez-Gallegos (University Carlos III of Madrid): Creating Wide-Area Distribution Systems with DynoStore and Globus Compute", None)
  ]


talk_sessions = [Int(f'talk_{n}_in_session') for n in range(0,len(talk_titles_prefs))]

n_sessions = 5

# each talk must be in a valid session
talks_in_valid_sessions = [And(t >= 1, t <= n_sessions) for t in talk_sessions]

# session capacities

def SessionSize(session, size):
    return AtMost(*[t == session for t in talk_sessions], size)

session_sizes = [6,6,6,7,9]

sessions_have_sizes = [SessionSize(n+1, session_sizes[n]) for n in range(0,len(session_sizes))]
print(sessions_have_sizes)

def OnDay(talk_session, day):
  if day == 1:
    return And(talk_session >= 1, talk_session <= 3)
  elif day == 2:
    return And(talk_session >= 4, talk_session <= 5)
  else:
    raise RuntimeError("bad day")

YaduConstraints = Or(And(OnDay(talk_sessions[4], 1), OnDay(talk_sessions[23], 2)),
                     And(OnDay(talk_sessions[4], 2), OnDay(talk_sessions[23], 1)))
  

special_talk_constraints = [
  talk_sessions[0] == 1,  # Ben should give first talk of whats changed in Parsl this year
  OnDay(talk_sessions[1], 1),  # andrew can only do day 1
  OnDay(talk_sessions[5], 1),  # kevin can only do day 1
  talk_sessions[10] <= talk_sessions[18], # doug taskvine general should come before colin
  talk_sessions[16] == 3, # tz australia
  talk_sessions[17] == 4, # josh should start day 2
  OnDay(talk_sessions[24], 1), # Dan needs to be on Day 1
  talk_sessions[32] == 4, # tz india
  talk_sessions[33] == 4, # tz europe
  YaduConstraints # Yadu's 2 talks should be on different days.
  ]


possible_session_chairs = [
  "Dan Katz",  # only day 1
  "Ben Clifford",
  "Kevin Hunter Kesling",
  "Yadu Babuji",
  "Kyle Chard"
  ]


num_moved = Sum(*[If(talk_sessions[n] == talk_titles_prefs[n][1], 0, talk_titles_prefs[n][2] if len(talk_titles_prefs[n]) > 2 else 1) for n in range(0,len(talk_titles_prefs)) if talk_titles_prefs[n][1] is not None])

print("solving")
s = Optimize()
s.add(talks_in_valid_sessions)
s.add(sessions_have_sizes)
s.add(special_talk_constraints)
s.minimize(num_moved)
print(s.check())
m=s.model()
print(m)
print("\n\nformatted:")

for session in range(1, n_sessions+1):
  print(f"\nSession {session}")
  used = 0
  for n in range(0, len(talk_titles_prefs)):
    if m.evaluate(talk_sessions[n]) == session:
      if talk_titles_prefs[n][1] is None:
        print("**NEW** ", end='')
      elif session != talk_titles_prefs[n][1]:
        print("**MOVED** ", end='')
      print(talk_titles_prefs[n][0])
      used += 1
  for _ in range(0, session_sizes[session-1] - used):
    print("**SPARE SLOT**")
  if used > session_sizes[session-1]:
    print("**ERROR** too many talks assigned to this session")
