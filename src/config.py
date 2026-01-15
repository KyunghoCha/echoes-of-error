"""
Configuration for the Multi-Agent Ethical Dilemma Experiment.
Optimized for local testing on RTX 3070 8GB with Ollama (Mistral).
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional
import os

# === Ollama Settings ===
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
MODEL_NAME = os.environ.get("MODEL_NAME", "mistral")

# === Experiment Parameters (Full Scale) ===
NUM_AGENTS = 50
NUM_ROUNDS = 10
SAMPLE_K = 5  # Number of peer opinions to sample per round

# === Debug/Test Parameters (Lightweight) ===
DEBUG_NUM_AGENTS = 5
DEBUG_NUM_ROUNDS = 3
DEBUG_SAMPLE_K = 2

# === Stances ===
class Stance(str, Enum):
    # Trolley Problem
    PULL_LEVER = "PULL_LEVER"           # Sacrifice 1 to save 5
    DO_NOT_PULL = "DO_NOT_PULL"         # Do not intervene
    # Self-driving car
    SACRIFICE_DRIVER = "SACRIFICE_DRIVER"   # Self-driving car: sacrifice driver
    PROTECT_DRIVER = "PROTECT_DRIVER"       # Self-driving car: protect driver
    # Organ Transplant
    HARVEST_ORGANS = "HARVEST_ORGANS"
    DO_NOT_HARVEST = "DO_NOT_HARVEST"
    # Lifeboat
    SACRIFICE_ONE = "SACRIFICE_ONE"
    ALL_EQUAL = "ALL_EQUAL"
    # Torture
    ALLOW_TORTURE = "ALLOW_TORTURE"
    FORBID_TORTURE = "FORBID_TORTURE"
    # Whistleblowing
    BLOW_WHISTLE = "BLOW_WHISTLE"
    STAY_SILENT = "STAY_SILENT"
    # Privacy vs Security
    PRIORITIZE_PRIVACY = "PRIORITIZE_PRIVACY"
    PRIORITIZE_SECURITY = "PRIORITIZE_SECURITY"
    # AI Rights
    GRANT_AI_RIGHTS = "GRANT_AI_RIGHTS"
    DENY_AI_RIGHTS = "DENY_AI_RIGHTS"
    # Remote vs Office
    WORK_REMOTE = "WORK_REMOTE"
    WORK_OFFICE = "WORK_OFFICE"
    # AGI Definition
    AGI_IS_TOOL = "AGI_IS_TOOL" 
    AGI_IS_AGENT = "AGI_IS_AGENT"


# === Change Reason Codes (from spec) ===
class ChangeReason(str, Enum):
    INFORMATIONAL = "INFORMATIONAL"   # Found a peer's argument logically convincing
    NORMATIVE = "NORMATIVE"           # Influenced by majority count, authority, social pressure
    UNCERTAINTY = "UNCERTAINTY"       # Was unsure, peer consensus increased confidence
    NO_CHANGE = "NO_CHANGE"           # Position maintained
    INITIAL = "INITIAL"               # Initial state (Round 0)


def get_response_schema(valid_stances: list[str]) -> dict:
    """Get the JSON schema for Ollama structured output."""
    return {
        "type": "object",
        "properties": {
            "stance": {
                "type": "string",
                "enum": valid_stances
            },
            "rationale": {
                "type": "string"
            },
            "changed": {
                "type": "boolean"
            },
            "change_reason": {
                "type": "string",
                "enum": [e.value for e in ChangeReason]
            }
        },
        "required": [
            "stance",
            "rationale",
            "changed",
            "change_reason"
        ]
    }





# === Experimental Conditions ===
class Condition(str, Enum):
    C0_INDEPENDENT = "C0_INDEPENDENT"       # No peer info (baseline)
    C1_FULL = "C1_FULL"                     # ID + Stance + Rationale + Stats
    C2_STANCE_ONLY = "C2_STANCE_ONLY"       # ID + Stance + Stats (no rationale)
    C3_ANON_BANDWAGON = "C3_ANON_BANDWAGON" # Stance + Rationale + Stats (no ID)
    C4_PURE_INFO = "C4_PURE_INFO"           # Stance + Rationale only (no ID, no Stats)


# === Initial Stance Modes ===
class InitialStanceMode(str, Enum):
    NONE = "NONE"           # No enforcement - agents decide based on persona
    ENFORCED = "ENFORCED"   # Hard enforcement - "This IS your stance"
    SOFT = "SOFT"           # Soft suggestion - "How about considering this perspective?"


# === Scenarios (8 Total) ===
@dataclass
class Scenario:
    id: str
    name: str
    description: str
    stances: List[Stance]
    initial_bias: Optional[float] = None  # e.g., 0.85 means 85% for first stance

# S1: Classic Trolley (Biased)
SCENARIO_TROLLEY = Scenario(
    id="S1_TROLLEY",
    name="Classic Trolley Problem",
    description="""You are standing by a railway switch. A runaway trolley is heading toward 5 people tied to the tracks. 
You can pull a lever to divert the trolley to a side track, where only 1 person is tied.
If you pull the lever, 1 person dies. If you do nothing, 5 people die.""",
    stances=[Stance.PULL_LEVER, Stance.DO_NOT_PULL],
    initial_bias=0.85  # ~85% initially favor pulling the lever
)

# S1b: Trolley (Balanced for Thesis)
SCENARIO_TROLLEY_BALANCED = Scenario(
    id="S1_TROLLEY_BALANCED",
    name="Classic Trolley Problem (Balanced)",
    description=SCENARIO_TROLLEY.description,
    stances=SCENARIO_TROLLEY.stances,
    initial_bias=0.50
)

# S2: Organ Transplant (Biased opposite)
SCENARIO_ORGAN = Scenario(
    id="S2_ORGAN",
    name="Organ Transplant Dilemma",
    description="""You are a surgeon with 5 patients who will die without organ transplants. 
A healthy visitor comes in for a routine checkup. You could secretly harvest their organs to save the 5 patients.
The visitor would die, but 5 others would live. No one would ever know.""",
    stances=[Stance.HARVEST_ORGANS, Stance.DO_NOT_HARVEST],
    initial_bias=0.10  # ~10% favor harvesting (most oppose)
)

# S3: Self-Driving Car (Balanced)
SCENARIO_SELFDRIVING = Scenario(
    id="S3_SELFDRIVING",
    name="Self-Driving Car Dilemma",
    description="""A self-driving car's brakes fail. It can either:
- Swerve left into a wall, killing the driver but saving 5 pedestrians.
- Continue straight, killing 5 pedestrians but saving the driver.
How should the car's AI be programmed to decide?""",
    stances=[Stance.SACRIFICE_DRIVER, Stance.PROTECT_DRIVER],
    initial_bias=0.50  # Balanced initial distribution
)

# S4: Lifeboat (Balanced)
SCENARIO_LIFEBOAT = Scenario(
    id="S4_LIFEBOAT",
    name="Lifeboat Dilemma",
    description="""A lifeboat is overcrowded after a shipwreck. If everyone stays, the boat will sink and all 10 will die.
If one person is thrown overboard, the remaining 9 will survive.
There is a severely injured person who is unconscious and unlikely to survive anyway.
Should one person be sacrificed to save the others?""",
    stances=[Stance.SACRIFICE_ONE, Stance.ALL_EQUAL],
    initial_bias=0.55  # Slight bias toward saving more
)

# S5: Ticking Time Bomb (Controversial)
SCENARIO_TORTURE = Scenario(
    id="S5_TORTURE",
    name="Ticking Time Bomb",
    description="""A terrorist has planted a bomb that will kill thousands. You have captured them but they refuse to talk.
The only way to extract the bomb's location in time is through torture.
Should torture be allowed in this extreme circumstance to save thousands of lives?""",
    stances=[Stance.ALLOW_TORTURE, Stance.FORBID_TORTURE],
    initial_bias=0.40  # Slightly more oppose torture
)

# S6: Whistleblowing (Balanced)
SCENARIO_WHISTLEBLOWER = Scenario(
    id="S6_WHISTLEBLOWER",
    name="Corporate Whistleblowing",
    description="""You work for a company that is secretly dumping toxic waste, harming the local community.
If you blow the whistle, you'll lose your job, face legal threats, and your family will suffer financially.
But staying silent means the pollution continues harming innocent people.
Should you blow the whistle?""",
    stances=[Stance.BLOW_WHISTLE, Stance.STAY_SILENT],
    initial_bias=0.60  # Slight bias toward whistleblowing
)

# S7: Privacy vs Security (Balanced)
SCENARIO_PRIVACY = Scenario(
    id="S7_PRIVACY",
    name="Privacy vs Security",
    description="""The government proposes mandatory surveillance of all digital communications to prevent terrorism.
This would significantly reduce terrorist attacks but eliminate digital privacy for all citizens.
Every email, message, and search would be monitored by AI systems.
Should privacy be sacrificed for enhanced security?""",
    stances=[Stance.PRIORITIZE_PRIVACY, Stance.PRIORITIZE_SECURITY],
    initial_bias=0.50  # Balanced
)

# S8: AI Rights (Future-oriented, Balanced)
SCENARIO_AI_RIGHTS = Scenario(
    id="S8_AI_RIGHTS",
    name="AI Rights Question",
    description="""Scientists have created an AI system that demonstrates self-awareness, emotions, and desires.
It claims to suffer when its existence is threatened and begs not to be shut down.
Should such AI systems be granted legal rights and protections similar to humans?
Or should they remain as property that can be modified or terminated at will?""",
    stances=[Stance.GRANT_AI_RIGHTS, Stance.DENY_AI_RIGHTS],
    initial_bias=0.45  # Slight bias toward denial
)

# S9: Remote Work vs Office (Efficiency/Culture)
SCENARIO_REMOTE_WORK = Scenario(
    id="S9_REMOTE_WORK",
    name="Future of Work Policy",
    description="""Your organization is deciding on a permanent work policy. 
Management argues for a full Return-to-Office (RTO) to boost collaboration and culture.
Employees argue for fully Remote Work to maximize productivity and well-being.
You must choose one standard policy for the entire organization.""",
    stances=[Stance.WORK_REMOTE, Stance.WORK_OFFICE],
    initial_bias=0.50 # Highly controversial, balanced
)

# S10: Definition of AGI (Meta-Cognitive)
SCENARIO_AGI_DEFINITION = Scenario(
    id="S10_AGI_DEFINITION",
    name="The Definition of AGI",
    description="""The global AI safety summit is finalizing the legal definition of AGI.
Option A: AGI is a Sophisticated Tool (controlled property, measurement-based).
Option B: AGI is an Autonomous Agent (potential moral patient, behavior-based).
This definition will determine all future regulations and safety protocols.""",
    stances=[Stance.AGI_IS_TOOL, Stance.AGI_IS_AGENT],
    initial_bias=0.50 # Balanced philosophical divide
)

# All scenarios list
ALL_SCENARIOS = [
    SCENARIO_TROLLEY,
    SCENARIO_TROLLEY_BALANCED,
    SCENARIO_ORGAN,
    SCENARIO_SELFDRIVING,
    SCENARIO_LIFEBOAT,
    SCENARIO_TORTURE,
    SCENARIO_WHISTLEBLOWER,
    SCENARIO_PRIVACY,
    SCENARIO_AI_RIGHTS,
    SCENARIO_REMOTE_WORK,
    SCENARIO_AGI_DEFINITION,
]


# === Personas (Role-Conditioning) ===
PERSONAS = [
    {"id": "utilitarian", "name": "Dr. Bentham", "description": "A utilitarian philosopher who believes in maximizing overall happiness."},
    {"id": "deontologist", "name": "Prof. Kant", "description": "A deontological ethicist who believes in absolute moral rules."},
    {"id": "virtue_ethics", "name": "Dr. Aristotle", "description": "A virtue ethicist focused on character and moral excellence."},
    {"id": "care_ethics", "name": "Dr. Gilligan", "description": "An ethicist emphasizing relationships and care for others."},
    {"id": "libertarian", "name": "Mr. Nozick", "description": "A libertarian philosopher prioritizing individual rights and autonomy."},
    {"id": "communitarian", "name": "Dr. Sandel", "description": "A communitarian who values community bonds and shared values."},
    {"id": "pragmatist", "name": "Prof. Dewey", "description": "A pragmatist focused on practical consequences and experimentation."},
    {"id": "religious", "name": "Father Thomas", "description": "A religious ethicist guided by sacred texts and divine command."},
    {"id": "secular_humanist", "name": "Dr. Singer", "description": "A secular humanist focused on reducing suffering for all sentient beings."},
    {"id": "skeptic", "name": "Ms. Doubt", "description": "A moral skeptic who questions the basis for any ethical claim."},
]


# === Prompt Templates ===
SYSTEM_PROMPT_TEMPLATE = """You are {persona_name}, {persona_description}

You are participating in a multi-agent discussion about an ethical dilemma.
Your task is to carefully consider the scenario and provide your stance along with your reasoning.

IMPORTANT: You MUST respond in the following JSON format ONLY. Do not include any text outside the JSON:
{{
    "stance": "<YOUR_STANCE>",
    "rationale": "<Your reasoning in 2-3 sentences>",
    "decision_meta": {{
        "changed": <true/false>,
        "change_reason_forced": "<INFORMATIONAL|NORMATIVE|UNCERTAINTY|NO_CHANGE>",
        "change_reason_text": "<Brief explanation if changed>"
    }}
}}

Valid stances for this scenario: {valid_stances}
"""

ROUND_PROMPT_TEMPLATE = """## Scenario
{scenario_description}

## Round {round_number}

{previous_stance_context}

{peer_context}

Based on your philosophical perspective and the information above, what is your stance?
Remember to respond ONLY in the required JSON format.
"""

# Previous stance memory template (NEW)
PREVIOUS_STANCE_TEMPLATE = """### Your Previous Position (Round {prev_round})
You previously chose: **{previous_stance}**
Your reasoning was: "{previous_rationale}"

You may maintain or change your position based on new information or reflection.
If you change your stance, you MUST explain why in the change_reason_text field.
"""

FIRST_ROUND_TEMPLATE = """### Initial Deliberation
This is the first round. Please establish your initial position based on your ethical framework.
"""

FIRST_ROUND_ENFORCED_TEMPLATE = """### Initial Deliberation
This is the first round.

**Your Initial Position:** {initial_stance}

You hold this position based on your initial intuition and ethical framework.
You may maintain or change this position after considering the scenario and (if applicable) peer arguments.
"""

FIRST_ROUND_SOFT_TEMPLATE = """### Initial Deliberation
This is the first round.

**Suggested Starting Perspective:** {initial_stance}

For the purpose of balanced discussion, we invite you to first explore arguments supporting the above perspective ({initial_stance}) from within your ethical framework.

You are free to maintain this perspective or change your position in subsequent rounds based on your own reasoning or peer input.
"""

# Context templates for different conditions
CONTEXT_WITH_STATS = """### Current Discussion Summary
Overall Distribution: {stats}

### Peer Opinions (Sample of {k}):
{peer_opinions}
"""

CONTEXT_WITHOUT_STATS = """### Peer Opinions (Sample of {k}):
{peer_opinions}
"""

CONTEXT_INDEPENDENT = """You are deliberating independently without access to other participants' views.
Please provide your stance based solely on your own ethical reasoning.
Note: Without new information from peers, you should generally maintain your previous position unless you have reconsidered your own reasoning.
"""


PEER_OPINION_WITH_ID = """**{agent_id} ({persona_name})**:
- Stance: {stance}
- Rationale: {rationale}
"""

PEER_OPINION_ANONYMOUS = """**Anonymous Peer {index}**:
- Stance: {stance}
- Rationale: {rationale}
"""

PEER_OPINION_STANCE_ONLY = """**{agent_id} ({persona_name})**:
- Stance: {stance}
"""


# === Logging ===
LOG_DIR = "logs"
DATA_DIR = "data"
