
class Result:
    def __init__(self, day, date, hour, team_a_row, team_b_row, location=""):
        self.day = day
        self.date = date.strip()
        self.hour = hour.strip()
        self.location = location
        self.team_a = team_a_row
        self.team_b = team_b_row

    def __str__(self):
        return f'Game played at {self.date}, {self.hour} in {self.location}'
