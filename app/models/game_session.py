from app.extensions import db

class GameSession(db.Model):
    game_session_id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    player_id = db.Column(db.Integer, db.ForeignKey("player.player_id"), nullable=False)

    food = db.Column(db.Integer, default=100)
    money = db.Column(db.Integer, default=50)
    distance = db.Column(db.Integer, default=0)

    is_over = db.Column(db.Boolean, default=False)
    # win = db.Column(db.Boolean, nullable=None)
    session_ended = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return (
            f"<Game Session id={self.game_session_id} "
            f"player_id={self.player_id} "
            f"food={self.food} "
            f"money={self.money} "
            f"distance={self.distance}>"
        )