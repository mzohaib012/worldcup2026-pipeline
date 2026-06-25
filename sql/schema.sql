DROP TABLE IF EXISTS match_goals;
DROP TABLE IF EXISTS matches;
DROP TABLE IF EXISTS players;
DROP TABLE IF EXISTS teams;
DROP TABLE IF EXISTS tournaments;

CREATE TABLE tournaments (
    tournament_id    VARCHAR(20) PRIMARY KEY,
    tournament_name  VARCHAR(150),
    host_country     VARCHAR(100),
    num_teams        INT
);

CREATE TABLE teams (
    team_id        VARCHAR(20) PRIMARY KEY,
    team_name      VARCHAR(100),
    team_code      VARCHAR(10),
    confederation  VARCHAR(50)
);

CREATE TABLE players (
    player_id            VARCHAR(20) PRIMARY KEY,
    full_name            VARCHAR(150),
    family_name          VARCHAR(100),
    given_name           VARCHAR(100),
    nationality_team_id  VARCHAR(20) REFERENCES teams(team_id),
    date_of_birth        DATE,
    position             VARCHAR(30),
    height_cm            INT,
    photo_url             VARCHAR(255)
);

CREATE TABLE matches (
    match_id      VARCHAR(30) PRIMARY KEY,
    tournament_id VARCHAR(20) REFERENCES tournaments(tournament_id),
    match_date    DATE,
    stage         VARCHAR(50),
    group_name    VARCHAR(20),
    home_team_id  VARCHAR(20) REFERENCES teams(team_id),
    away_team_id  VARCHAR(20) REFERENCES teams(team_id),
    home_score    INT,
    away_score    INT,
    venue         VARCHAR(150),
    city          VARCHAR(100),
    country       VARCHAR(100),
    result        VARCHAR(20),
    api_match_id  VARCHAR(50)
);

CREATE TABLE match_goals (
    goal_id          VARCHAR(30) PRIMARY KEY,
    match_id         VARCHAR(30) REFERENCES matches(match_id),
    player_id        VARCHAR(20) REFERENCES players(player_id),
    team_id          VARCHAR(20) REFERENCES teams(team_id),
    minute           INT,
    minute_stoppage  INT,
    is_penalty       BOOLEAN DEFAULT FALSE,
    is_own_goal       BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_matches_tournament ON matches(tournament_id);
CREATE INDEX idx_goals_player ON match_goals(player_id);
CREATE INDEX idx_goals_match ON match_goals(match_id);