# TODOs for parslfest 2025
# maybe put in some session constraints on a mix of remote and in person, as there is a lot of remote this time?

from z3 import *

# numbers will be represented as bitvecs with this
# many bits - so user must manually make sure its big enough
# to hold results.
BITFIELD = 4

# how much we care about schedule stickiness
stickiness_factor = False

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

    # APeX 2026

    #0
    ("Ben Clifford", None, 0, ["community", "parsl"], "Parsl Community Grants Closing Roundup", False),
    ("Ben Clifford", None, 0, ["parsl", "insides"], "Formal methods for Parsl block shutdown", False),
    ("Stephen Hudson", None, 0, ["agents", "multisite", "infrastructure"], "AgentLab: Collaborative Agentic Campaigns across HPC Facilities", True),
    ("David Abramov", None, 0, ["agents"], "Agentic Workflows for Tomography and Knowledge Curation", False),
    ("Daniel Rosendo", None, 0, ["agents", "biology"], "An Agentic AI Framework to Accelerate Scientific Discovery in Plant Phenotyping", True),
    ("Matt Baughman", None, 0, ["agents", "physics/chemistry"], "Tritium Splash: Using Agents to Drive Large-Scale Exploration of Multiphysics Simulations for Fusion Fuels", True),
    ("Max Burnette", None, 0, [], "Diamond Platform", False),
    ("Amal Gueroudji", None, 0, ["agents", "observability", "provenance"], "Provenance Collection for Agentic frameworks", True),
    ("Owen Price-Skelly", None, 0, ["agents", "physics/chemistry"], "Self-steering MLIP Committee with Rootstock and Academy Agents", True),
    ("Chris Harrop", None, 0, ["agents", "earth"], "Academy Agents for Numerical Weather Prediction", False),
    #10 

    ("Logan Ward", None, 0, ["physics/chemistry", "agents"], "Agentic AI-Driven Molecule Design on HPC", False),
    ("Chandrachur Bhattacharya", None, 0, ["agents"], "AISAC", False),
    ("Valesca Moura", None, 0, ["agents", "observability", "provenance"], "Instrumentation vs. Observability: Provenance Capture Trade-offs in Agentic Workflows", False),
    ("Valerie Hayot-Sasson", None, 0, ["tools+techniques"], "Continuous reproducibility with Correct", False),
    ("Geoffrey Lentner", None, 0, ["Globus Compute", "site"], "The Anvil MEP and building on top of Globus Compute", True),
    ("Mike Tynes", None, 0, [], "TBD", True),
    ("Alex Brace", None, 0, ["agents", "physics/chemistry"], "DeepDriveWE: An agentic approach to enhanced sampling molecular dynamics", True),
    ("Haotian Xie", None, 0, ["agents"], "Diamond Agents", True),
    ("Tim Dunn", None, 0, [], "TBD", False),
    ("Suman Raj", None, 0, ["infrastructure"], "Fairness-Aware Scheduling for Bursty HPC Workloads", True),

    #20
    ("Matt Sinclair", None, 0, ["agents", "biology"], "Federated deployment of an agentic biology framework at scale", False),
    ("Harikrishna Tummalapalli", None, 0, ["parsl", "site"], "Ensemble Executor for Insane-Scale Compute", True),

    #unregistered - assume remote
    ("Alex Zhang", None, 0, ["agents", "tools+techniques"], "Per-action Authorization for Shared Agents", False),

    # unregistered - assume remote
    ("Ryan Chard", None, 0, ["agents", "tools+techniques"], "Reputation as Community Memory for the Agentic Web", False),

    ("Augustus Ellerm", None, 0, [], "HPCBridge", False),
    ("Alok Kamatar", None, 0, [], "TBD", True),

    # unregistered - assume in person
    ("Yadu Babuji", None, 0, ["agents", "observability", "tools+techniques"], "Academy Dashboard", True),

    # unregistered - assume remote
    ("Kevin Hunter Kesling", None, 0, ["Globus Compute"], "TBD", False),

    # haochen not giving a talk...
    # ("Haochen Pan", None, 0, ["infrastructure"], "Resilient parallel workflows", True),
    
    ("Seena VazifeDunn", None, 0, ["Globus Compute", "multisite"], "Globus Tunnels + Compute", True),

    ("Himanshi Yadav", None, 0, ["agents", "text"], "Atomizing the Chicago Assyrian Dictionary: Agentic Workflow for Structuring Multi-Language Text Documents", True),

    #30
    ("Mihael Hategan", None, 0, ["agents", "tools+techniques"], "Reactive programming with Academy", False),
    ("Saiful Islam", None, 0, ["packaging", "infrastructure"], "Floability Backpacks: Packaging Workflows for Portable HPC Deployment", True),
    ("Kyle Chard", None, 0, ["intro"], "Welcome To APeX", True),
    ("Chris Janidlo", None, 0, ["parsl", "Globus Compute", "insides"], "HTEX Protocol compatibility", True),
  ]


talk_sessions = [BitVec(f'talk_{n}_in_session', BITFIELD) for n in range(0,len(talk_titles_prefs))]

# two different session structures: 2 bigger sessions, or 3 smaller sessions, per day
# session_sizes = [9,9,9,9]
session_sizes = [6,6,6,6,6,6]

# TODO: some assert on session sizes here: if the sessions are too big, we can't
# schedule n-1..n sized sessions.

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
    return And(AtMost(*[t == session for t in talk_sessions], size),
               AtLeast(*[t == session for t in talk_sessions], size-1),
              )

sessions_have_sizes = [SessionSize(n+1, session_sizes[n]) for n in range(0,len(session_sizes))]

def OnDay(talk_session, day):
  if day == 1:
    return And(talk_session >= 1, talk_session <= 3)
  elif day == 2:
    return And(talk_session >= 4, talk_session <= 6)
  else:
    raise RuntimeError("bad day")

special_talk_constraints = [
   talk_sessions[32] == 1, # Kyle must talk first for introduction

   Or(talk_sessions[6] == 1, OnDay(talk_sessions[6], 2)),  # by email:  if possible I?d like to avoid being scheduled between 3 - 3:45 Central on the 14th.

   OnDay(talk_sessions[19], 1),  # Could you please schedule my talk on Sept 14 if possible?

   OnDay(talk_sessions[0], 1), # ben's two talks on different days
   OnDay(talk_sessions[1], 2), # with the community one first

   Or(talk_sessions[16] == 1, talk_sessions[16] == 3),  # If possible, can I get a Monday (Sep 14th) slot? ?anytime except between 2-3pm works.

   OnDay(talk_sessions[30], 1),  # the 14th is the only option.

   talk_sessions[29] != 4  # just a preference for a time slot after 10 am

   # OnDay(talk_sessions[5], 1),  # Josh can only do day 1 in person
   # talk_sessions[5] != talk_sessions[0], # GC intro should not be in same session as Parsl intro 
   #talk_sessions[5] <= talk_sessions[6], # GC intro should come before other GC talks

   # these are deliberately different, due to content
   #talk_sessions[0] > 3,  # 3-languages talk should be on day 2
   #talk_sessions[31] !=  3, # Ben doesn't want to talk in TZ inconvenient times about monitoring
   #talk_sessions[0] > talk_sessions[31],  # ben's two talks should be in different sessions, and talk 31, being more serious, should come earlier?

   #talk_sessions[34] >= talk_sessions[22],  # academy app talk should be after greg's main academy talk
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
  "Chair A",  #0
  "Chair B",  #1
  "Chair C",  #2
  "Chair D",  #3
  "Chair E",  #4
  "Chair F",  #5
  ]

# session numbers here start at 0, not 1
sticky_session_chairs = [None, None, None, None, None, None]
# sticky_session_chairs = [0, 2, 4, 3, 1, 5]

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
  # session_chairs[0] != 1,  # Chris first time chair, so make two sessions happen before he chairs to get vibe
  # session_chairs[1] != 1,  # "
  ]

for sc_n in range(0, len(possible_session_chairs)):
  print(f"Excluding talks for possible session chair {sc_n} -- {possible_session_chairs[sc_n]}")
  for ses_n in range(0, len(talk_titles_prefs)):
    if talk_titles_prefs[ses_n][0] == possible_session_chairs[sc_n]:
      print(f"Excluding speaker for talk {ses_n} from session {sc_n}")
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
            And(num_in_person >= 3, num_in_person <=3, num_in_session == 6),
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

if stickiness_factor:
  objective_function = num_moved
  s.minimize(objective_function)

# session chairs are sticky
# for n in range(n_sessions):
#  if sticky_session_chairs[n] is not None:
#    s.add_soft(session_chairs[n] == sticky_session_chairs[n], weight="0.1")

def format_solution(m):
 print("\n\nformatted:")


 for session in range(1, n_sessions+1):
  if session == 1:
    print("\n\n**** DAY 1 ****")
  if session == 4:
    print("\n\n**** DAY 2 ****")
  chairname = possible_session_chairs[m.evaluate(session_chairs[session - 1]).as_long()]
  print(f"\nSession {session} - chair {chairname}")
  used = 0
  for n in range(0, len(talk_titles_prefs)):

    if m.evaluate(talk_sessions[n]) == session:
      if talk_titles_prefs[n][1] is None:
        # print("**NEW** ", end='')
        pass
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


import time
start= time.time()
def hook(m):
  print(f"callback: (time {time.time()-start})")
  print("=== objectives ===")
  for o in s.objectives():
    print(m.evaluate(o))
  print("=== formatted solution ===")
  format_solution(m)

s.set_on_model(hook)

print("solving")
result = s.check()

print(result)

if result == unsat :
    print(s.unsat_core())
    raise RuntimeError("Cannot schedule APeX 2026 :(")

m=s.model()
print(m)
print("objectives:")
print(s.objectives())
print("sexpr:")
print(s.sexpr())
print("stats:")
print(s.statistics())
format_solution(m)

