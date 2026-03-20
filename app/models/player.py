from app.extentions import db

class Player(db.Model):
    player_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    player_name = db.Column(db.String(12), unique=True, nullable=False)
    game_sessions = db.relationship("GameSession", backref="player")

    def __repr__(self):
        return f"<Player {self.player_id} - {self.player_name}>"