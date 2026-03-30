🕹️ Silicon Valley Trail

A terminal-based simulation game inspired by *The Oregon Trail*, where a startup team journeys from San Jose to San Francisco to present at Demo Day.

Players must manage limited resources, navigate dynamic events, and make strategic decisions to successfully reach their final pitch.

---

🚀 How to Run

Set a free [OpenWeatherMap](https://openweathermap.org/api) API key (Current Weather Data). Either export it or put `OPENWEATHERMAP_API_KEY=...` in a `.env` file at the **project root** or in **`app/.env`** (both are gitignored).

```bash
export OPENWEATHERMAP_API_KEY="your_key_here"
python app/silicon_valley_trail_backend.py
```

If the key is unset, travel still works using random simulated weather (same as when the API request fails).

---

🎯 Objective

Reach San Francisco and successfully deliver your final pitch.

---

🧠 Core Gameplay

Each day, the player chooses an action:

* 🚗 **Travel** → move forward, consume resources, trigger events
* 🥱 **Rest** → recover morale and some fuel
* ⚡️ **Debug** → reduce bugs at the cost of morale and cash

---

📊 Resources

Players must manage four core resources:

* 💵 **Cash** → required for recovery actions and events
* ⛽️ **Fuel** → required to travel between locations
* 🥳 **Morale** → affects team readiness and final pitch success
* 👾 **Bugs** → impacts product stability and demo outcome

---

🌍 Map Progression

San Jose → Santa Clara → Palo Alto → Redwood City → Mountain View → San Mateo → Daly City → San Francisco

*(Additional location planned to expand to 10 total nodes)*

---

⚡ Event System

* Events trigger based on player actions
* Weighted randomness ensures balanced gameplay
* Optional events introduce player choice and tradeoffs

Examples:

* 🚧 Roadwork → fuel loss + bugs increase
* 🛞 Flat tire → fuel + cash penalty
* 💻 Hackathon → high risk / high reward
* ✈️ Supply drop → boosts all resources

---

🛒 Costco System

* Available at select locations
* One-time use per location
* High-cost, high-reward recovery option

---

🌦️ Weather System (API-Driven)

Weather data is fetched from the OpenWeatherMap API and affects gameplay:

* ☀️ Clear → slight morale boost
* 🌧️ Rain → morale penalty
* 🌫️ Fog → minor disruption
* 🥵 Heat → increased fuel consumption + morale drop

If the key is missing, the request fails, or the response is invalid, the game falls back to simulated weather conditions.

---

🏁 Win / Lose Conditions

### Win:

* Reach San Francisco
* Successfully complete the final pitch

### Lose:

* Run out of fuel
* Run out of cash
* Morale reaches zero
* Too many bugs cause demo failure
* Unable to reach final destination due to resource constraints

---

🧪 Testing (Planned)

A test suite will be implemented to validate:

* Resource boundary conditions
* Travel and event interactions
* Endgame scenarios and failure states

Testing will be developed using Cursor to ensure reliability and maintainability.

---

🧠 Design Highlights

* Clear separation of systems:

  * Weather = environment effects
  * Events = team-driven outcomes
* Focus on meaningful resource tradeoffs
* Guardrails to prevent soft-lock scenarios
* Incremental complexity with maintainable structure

---

⚖️ Tradeoffs

* Prioritized gameplay clarity over feature bloat
* Used API fallback to ensure consistent playability
* Kept architecture simple and readable for extensibility

---

🤖 AI Usage

Tools like Cursor and ChatGPT were used for ideation, debugging, and architectural guidance while maintaining full understanding and ownership of the implementation.

---

🚀 Future Improvements

* Add additional location(s) to expand gameplay
* Improve balancing of events and resource flow
* Enhance CLI UI/UX with richer formatting
* Expand test coverage

