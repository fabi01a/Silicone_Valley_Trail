🕹️ Silicon Valley Trail 🌲

A terminal-based simulation game inspired by The Oregon Trail and the Silicon Valley series.

You play as Richard Hendricks, leading your team - Gilfoyle and Dinesh - on a journey from San Jose to San Francisco to pitch your latest startup to a group of investors.

Along the way, you’ll manage resources, survive unpredictable events, and try to keep your team (and your product) from falling apart.

Will you make it to San Francisco with enough fuel, morale, and cash?  
Can Gilfoyle keep the car running?  
Will Dinesh sabotage the presentation?

Play the game and find out.


---
## 👾 Game Play


https://github.com/user-attachments/assets/7ff1c8ee-72db-43cc-a611-78ba75d84ba6



https://github.com/user-attachments/assets/8cf228ee-dde7-4d2a-b747-a3639033a638



---
## 🚀 Quick Start (from a fresh machine)

### 1. Clone the repo
```bash
git clone <your-repo-url>
cd silicon-valley-trail
```

### 2. Create a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
# or
venv\Scripts\activate     # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

Core dependencies:
- blessed → terminal UI  
- requests → API calls  
- python-dotenv (optional, for local env loading)

### 4. Set up your API key (optional but recommended)

This project uses the OpenWeatherMap API

**Option A: `.env` file (recommended)**

Create a `.env` file in either:
- project root  
- `app/.env`

```env
OPENWEATHERMAP_API_KEY=your_api_key_here
```

**Option B: environment variable**

```bash
export OPENWEATHERMAP_API_KEY=your_api_key_here
```

### 5. Run the game
```bash
python app/silicon_valley_trail_backend.py
# or
python -m app.silicon_valley_trail_backend
```


---
### 🧪 Run without API (mock mode)

No API key? No problem.  
The game will automatically fall back to random weather simulation.

```bash
unset OPENWEATHERMAP_API_KEY
python app/silicon_valley_trail_backend.py
```


---
## 🎮 Example Gameplay

<img width="459" height="244" alt="Screenshot" src="https://github.com/user-attachments/assets/ae68bcf2-2388-4d42-9689-36693344d411" />

## 🎪 Example Event

<img width="391" height="114" alt="Screenshot" src="https://github.com/user-attachments/assets/cb6890a2-5ce5-493b-a728-0d25fe9fa7e9" />


---
## 🏗️ Architecture Overview

➡️ Core structure

<img width="530" height="170" alt="Screenshot 2026-03-31 at 7 23 07 PM" src="https://github.com/user-attachments/assets/bda08375-7c6e-4ae7-98ae-a335a409000c" />


➡️ Key Design Principle

- State-driven architecture  
- Everything flows through: `GameState`  
- No hidden globals, no scattered state mutations  


---
## 📦 Data Modeling

➡️ GameState (core model)

Tracks:
- resources → cash, fuel, morale, bugs  
- progression → progress_index, current_location  
- flags → visited_costco, visited_restaurants  
- outcome → is_over, win  

➡️ Events

- Defined as data + behavior  
- Weighted selection (`random.choices`)  
- Optional events prompt the user  

```python
{
  "name": "Hackathon",
  "applies_to": {"travel"},
  "optional": True,
  "weight": 2,
}
```

➡️ Persistence

Currently:
- In-memory only  
- Designed to be extendable later  


---
## 🌦️ Design Notes (API + Gameplay)

👉 Why weather?

I chose a live API because:
- adds real-world variability  
- makes runs feel less deterministic  
- introduces subtle strategy shifts  

➡️ Gameplay impact

<img width="410" height="108" alt="Screenshot 2026-03-31 at 7 21 07 PM" src="https://github.com/user-attachments/assets/393a3de0-73b2-4b99-80bf-c03ca459add0" />



➡️ Fallback Design

If API fails:

👉 game switches to random weather  

This ensures:
- no broken gameplay  
- no dependency on network  


---
## ⚠️ Error Handling

➡️ Network failures:

```python
except Exception:
    condition = random.choice(...)
```

→ seamless fallback  

➡️ Missing API Key
- automatically uses mock weather  
- no crashes or warnings  

➡️ Input validation
- All prompts enforce `(y/n)`  
- Retry loops prevent invalid input  


---
## ⚖️ Tradeoffs

1. Simplicity vs realism  
- chose lightweight simulation  
- avoided overcomplicating economy  

2. In-memory state  
- faster iteration  
- easier testing  
- not persistent (intentional)  

3. High event probability  

```python
TRAVEL_RANDOM_EVENT_CHANCE = 0.85
```

- keeps gameplay dynamic  
- slightly less realistic, more fun  

4. API abstraction  
- weather affects fuel + morale  
- avoids tight coupling  


---
## 🔍 Test Suite Overview

➡️ Covers core gameplay mechanics:

- GameState → syncing + boundaries  
- Travel → progression + fuel checks  
- Weather → API + fallback  
- Events → resource changes  
- Actions → constraints + updates  
- Final pitch → win/lose logic  

➡️ Mocking Strategy
- API calls mocked (`unittest.mock`)  
- randomness controlled for deterministic tests  


---
## 🧠 Design Philosophy

- clean backend system design  
- modular architecture  
- predictable state transitions  
- readable CLI UX  


---
## 🤖 AI Usage

Cursor was used to scaffold parts of the game and test suite.  
ChatGPT was used to break down logic, debug, and refine system design.


---
## 💬 Final Thoughts

This started as a simple CLI game and evolved into a system design exercise:

- managing complexity  
- enforcing boundaries between systems  
- balancing gameplay vs logic  

⏳ If I had more time:
- persistence (save/load runs)  
- richer event chains  
- difficulty modes  
- UI upgrades  
