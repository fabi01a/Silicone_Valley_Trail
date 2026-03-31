🕹️ Silicon Valley Trail 🌲

A terminal-based simulation game inspired by The Oregon Trail and the Silicon Valley series.

You play as Richard Hendricks, leading your team - Gilfoyle and Dinesh - on a journey from San Jose to San Francisco to pitch your latest startup to a group of investors.

Along the way, you’ll manage resources, survive unpredictable events, and try to keep your team (and your product) from falling apart.

Will you make it to San Francisco with enough fuel, morale, and cash?
Can Gilfoyle keep the car running?
Will Dinesh sabotage the presentation?

Play the game and find out.

-----


## 🚀 Quick Start (from a fresh machine)

### 1. Clone the repo
``` bash
   git clone <your-repo-url>
   cd silicon-valley-trail
```
   
### 2. Create a virtual environment
 ``` bash
    python3 -m venv venv
    source venv/bin/activate  # Mac/Linux
    # or
    venv\Scripts\activate     # Windows
```
### 3. Install dependencies
``` bash 
   pip install -r requirements.txt
```
   Core dependencies:
   • blessed → terminal UI
   • requests → API calls
   • vpython-dotenv (optional, for local env loading)

6. Set up your API key (optional but recommended)
   This project uses the OpenWeatherMap API
  • Option A: .env file (recommended)
  
  Create a .env file in either:
     • project root OR
     • app/.env
     $ OPENWEATHERMAP_API_KEY=your_api_key_here

  ### • Option B: environment variable
  ``` bash
     export OPENWEATHERMAP_API_KEY=your_api_key_here
   ```

### 5. Run the game
``` bash
   python app/silicon_valley_trail_backend.py
   # or
   python -m app.silicon_valley_trail_backend
``` bash

 -----

### 🧪 Run without API (mock mode)
No API key? No problem.
The game will automatically fall back to random weather simulation, so you can still play fully:
``` bash
 unset OPENWEATHERMAP_API_KEY
 python app/silicon_valley_trail_backend.py
```

 -----


 🎮 Example Gameplay
 
   <img width="459" height="244" alt="Screenshot 2026-03-31 at 10 21 38 AM" src="https://github.com/user-attachments/assets/ae68bcf2-2388-4d42-9689-36693344d411" />

 
 🎪 Example Event

 <img width="391" height="114" alt="Screenshot 2026-03-31 at 10 22 07 AM" src="https://github.com/user-attachments/assets/cb6890a2-5ce5-493b-a728-0d25fe9fa7e9" />


 -----


  🏗️ Architecture Overview
  
  ➡️ Core structure
  
   <img width="544" height="383" alt="Screenshot 2026-03-31 at 10 21 05 AM" src="https://github.com/user-attachments/assets/93f56690-a20c-4545-a8b7-0cfa3f106619" />

 
 ➡️ Key Design Principal
    • State-driven architecture
    • Everything flows through: GameState
      (No hidden globals, no scattered state mutations)

 -----

 
 📦 Data Modeling
 
 ➡️ GameState (core model)
    Tracks:
    • resources → cash, fuel, morale, bugs
    • progression → progress_index, current_location
    • flags → visited_costco, visited_restaurants
    • outcome → is_over, win
  
 ➡️ Events
    • Defined as data + behavior
    • Weighted selection (random.choices)
    • Optional events prompt the user

   {
     "name": "Hackathon",
     "applies_to": {"travel"},
     "optional": True,
     "weight": 2,
   }

  ➡️ Persistence
     Currently:
     • In-memory only
     • Designed to be extendable (DB or file persistence later)

   -----


   🌦️ Design Notes (API + Gameplay)
   
   👉🏼 Why weather?

   I chose a live API because:
    • adds real-world variability
    • makes runs feel less deterministic
    • introduces subtle strategy shifts

   ➡️ Gameplay impact
      Weather affects:

   <img width="476" height="195" alt="Screenshot 2026-03-31 at 10 24 52 AM" src="https://github.com/user-attachments/assets/e585f003-4f50-4c8c-93ff-ffbd8c8b99ef" />

  
   ➡️ Fallback Design
      If API fails:

   👉🏼 game switches to random weather

   This ensures:
    • no broken gameplay
    • no dependency on network

   -----


   ⚠️ Error Handling
  
   👉🏼 Scenarios:
   
   ➡️ Network failures:
   ``` bash
  
   except Exception:
    condition = random.choice(...)
   ```

   → seamless fallback

   ➡️ Missing API Key
     • automatically uses mock weather
     • no crashes or warnings

   ➡️ Input validation
      • All prompts enforce: (y/n)
      • with retry loops: ⚠️ Please enter 'y' or 'n'

   -----


   ⚖️ Tradeoffs
   
   1. Simplicity vs realism
      • chose lightweight simulation
      • avoided overcomplicating economy or physics
      
   2. In-memory state
      • faster iteration
      • easier testing
      • not persistent (intentional for scope)

   3. High event probability
      $ TRAVEL_RANDOM_EVENT_CHANCE = 0.85
      • keeps gameplay dynamic
      • slightly less “realistic,” more fun
   
   4. API abstraction
      • weather only affects fuel + morale 
      • avoids coupling API too tightly to game logic

   -----
   

   🔍 Test Suite Overview

   ➡️ Covers core gameplay mechanics:
   
   ✅ GameState
     • location syncing
     • boundary conditions
    
   ✅ Travel system
     • progression
     • fuel constraints
     • final leg guardrail
    
   ✅ Weather system
     • API mapping
     • fallback behavior
    
   ✅ Events
     • resource deltas
     • side effects
    
   ✅ Actions
     • rest/debug constraints
     • resource updates
    
   ✅ Final pitch
     • win/lose conditions

   ➡️ Mocking Stategy
     • API calls mocked via unittest.mock
     • randomness controlled for deterministic tests

   -----


   🧠 Design Philosophy
      This project focuses on:
      • clean backend system design
      • modular architecture
      • predictable state transitions
      • readable CLI UX

   -----


   🤖 AI USAGE
      Cursor was used to build out the framework of the game as well as test suite, ChatGPT was used to break down Cursor's work and fill in any 'missing' data not       acheived through Cursor

   -----
   

   💬 Final Thoughts
      This started as a simple CLI game and evolved into a system design exercise:
      • managing complexity
      • enforcing boundaries between systems
      • balancing gameplay vs logic
      

   ⏳ If I had more time, I’d explore:
      • persistence (save/load runs)
      • richer event chains
      • difficulty modes
      • UI upgrades
