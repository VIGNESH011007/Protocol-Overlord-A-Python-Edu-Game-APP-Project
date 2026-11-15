# Protocol-Overlord-A-Python-Edu-Game
Protocol Overlord: A Python Edu-Game is a story-driven desktop RPG built with Python, Tkinter, and SQLite. Uniting an AI assistant with elemental heroes to defeat a rogue digital virus, it pairs a 4-act story with 15 Python levels, randomized quiz battles, AI hints, custom Canvas avatars, SQLite save persistence, and a 20-question timed boss fight.


# Protocol Overlord: A Python Edu-Game

**Protocol Overlord** is a story-driven desktop educational RPG built with Python, Tkinter, and SQLite. Uniting an AI tactical assistant with elemental cyber-ninja heroes to stop a rogue digital virus, the game pairs an interactive 4-act storyline with 15 progressive Python programming levels, randomized quiz battles, custom vector graphics, and a timed firewall boss showdown.

---

## Key Features

- **4-Act Paced Story Intro:** Typewriter-style narrative dialogue accompanied by custom vector-drawn character portraits rendered directly on the Tkinter `Canvas`.
- **15 Progressive Python Levels:** Structured concept briefings advancing gradually from fundamentals to intermediate and advanced programming topics.
- **Anti-Cheat Randomized Battles:** Each regular level draws **7 random questions** from a 12-question bank and shuffles all answer choices on every attempt.
- **AI Tactical Hint System:** On-demand hints during combat help learners reason through syntax and logic problems without giving away the answer immediately.
- **Level 15 Firewall Boss Fight:** A high-stakes **20-question timed showdown** drawing across all 14 prior levels to purge the Digital Overlord's virus.
- **Synthesized Audio & Persistent Progress:** Built-in sound effects for combat feedback and automatic SQLite save tracking for unlocked levels, defeated enemies, and high scores.

---

## Curriculum Roadmap (15 Levels)

| Level | Topic | Core Concepts Covered |
| :--- | :--- | :--- |
| **01** | Variables & Output | `print()`, identifiers, comments, dynamic binding |
| **02** | Data Types & Casting | `int`, `float`, `str`, `bool`, `type()`, type conversion |
| **03** | Operators & Math Logic | `+`, `-`, `*`, `/`, `//`, `%`, `**`, operator precedence |
| **04** | Strings & Slicing | Indexing, slicing `[start:stop:step]`, f-strings, string methods |
| **05** | Conditionals | `if`, `elif`, `else`, logical operators (`and`, `or`, `not`) |
| **06** | Lists & Tuples | Mutability vs. immutability, `.append()`, `.pop()`, slicing |
| **07** | Loops (`for` & `while`) | `range()`, iteration, `break`, `continue`, `enumerate()` |
| **08** | Dictionaries & Sets | Key-value mapping, `.get()`, `.items()`, unique sets |
| **09** | Functions & Scope | `def`, `return`, default parameters, `*args`, `**kwargs`, local scope |
| **10** | Comprehensions & Built-ins | List/dict comprehensions, `zip()`, `any()`, `all()`, `sorted()` |
| **11** | Exception Handling | `try`, `except`, `else`, `finally`, `raise`, built-in exceptions |
| **12** | File I/O & JSON | `with open()`, read/write/append modes, `json.loads()`, `json.dumps()` |
| **13** | Recursion & Algorithms | Base cases, call stack, `O(log n)` Binary Search, Big-O complexity |
| **14** | Object-Oriented Programming | `class`, `__init__`, `self`, inheritance, `super()`, polymorphism |
| **15** | **Boss: Overlord Firewall** | **20 randomized questions across Levels 1–14 under a 4-minute timer** |

---

## Tech Stack

- **Language:** Python 3.x
- **GUI Framework:** `tkinter` (Standard Library)
- **Database:** `sqlite3` (Local persistent storage via `stark_ninjago_save.db`)
- **Audio & Utilities:** `winsound`, `random`, `math`

---

## How to Run

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/VIGNESH011007/Protocol-Overlord.git](https://github.com/VIGNESH011007/Protocol-Overlord.git)
   cd Protocol-Overlord

   Run the application:
No external packages or pip install steps are required—everything runs using Python's built-in standard libraries:

Bash
python ninjago_stark_quest.py
(Note: To reset campaign progress for a fresh playthrough, delete the generated stark_ninjago_save.db file and relaunch the script.)


### Quick Tip for Adding It on GitHub
Once you click **Create repository**, click on `README.md` in your new repo, click the **pencil (Edit)** icon in the top-right corner of the file preview, paste this text in, and click **Commit changes**.
