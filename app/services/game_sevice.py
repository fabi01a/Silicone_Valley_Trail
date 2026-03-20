from app import db
from app.models.game_session import GameSession
from app.models.player import Player

def create_game_session(
        player_id: int,
):
    new_game = GameSession(
        player_id=player_id
    )

    db.session.add(new_game)
    db.session.commit()
    return new_game