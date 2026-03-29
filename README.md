🕹️ Silicon Valley Trail

A terminal-based simulation game inspired by The Oregon Trail, where a startup team journeys from San Jose to San Francisco to present at Demo Day.

Players must manage limited resources, navigate unpredictable events, and make strategic decisions to successfully reach their final pitch.

🚀 How to Run
python app/silicon_valley_trail_backend.py
🎯 Objective

Reach San Francisco and successfully deliver your final pitch.

🧠 Core Gameplay

Each day, the player chooses an action:

Travel → move forward, consume resources, trigger events
Rest → recover morale and some fuel
Debug → reduce bugs but costs morale
📊 Resources

Players must manage:

Cash 💵 → used for events and supplies
Fuel ⛽ → required to travel between locations
Morale 🥳 → affects team performance
Bugs 👾 → impacts final pitch success
🌍 Map Progression

San Jose → Palo Alto → Mountain View → Redwood City → San Francisco

⚡ Events System
Events are triggered each turn based on action
Weighted randomness ensures balanced gameplay
Some events are optional (e.g., Hackathons, Supply Runs)

Examples:

🚧 Roadwork → reduces fuel and morale
🛞 Flat tire → costs fuel and cash
💻 Hackathon → high risk / high reward
🛒 Supply run → refuel and recover at a cost
🌦️ Weather System (Mocked)

Weather impacts gameplay:

Heat → higher fuel usage, morale drop, more bugs
Rain/Fog → minor penalties
Clear skies → small morale boost

--->(Designed to integrate with a real weather API)

🏁 Win / Lose Conditions

Win:

Reach San Francisco
Successfully complete final pitch

Lose:

Fuel runs out before destination
Cash or morale collapse
Too many bugs cause demo failure

🧪 Testing
----->
xxxxxxxxcccc

🧠 Design Notes (Draft)
Focused on resource pressure to create meaningful decisions
Used weighted randomness to balance event frequency
Introduced optional events to increase player agency
Added a final stretch checkpoint to encourage planning before endgame
Simplified system by removing unnecessary complexity (e.g., hype stat)
⚖️ Tradeoffs
Kept game loop simple instead of adding complex branching systems
Used mocked APIs first to ensure reliability and speed of development
Prioritized gameplay clarity over feature quantity
🤖 AI Usage

(Cursor / ChatGPT assisted with ideation, debugging, and structuring logic while maintaining full understanding and ownership of implementation.)
