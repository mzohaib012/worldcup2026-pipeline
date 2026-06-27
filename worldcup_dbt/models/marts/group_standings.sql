WITH team_matches AS (
    SELECT
        tournament_id, group_name, home_team_id AS team_id,
        home_score AS goals_for, away_score AS goals_against,
        CASE WHEN home_score > away_score THEN 'win'
             WHEN home_score = away_score THEN 'draw'
             ELSE 'loss' END AS result
    FROM {{ source('worldcup', 'matches') }}
    WHERE group_name IS NOT NULL AND home_score IS NOT NULL

    UNION ALL

    SELECT
        tournament_id, group_name, away_team_id AS team_id,
        away_score AS goals_for, home_score AS goals_against,
        CASE WHEN away_score > home_score THEN 'win'
             WHEN away_score = home_score THEN 'draw'
             ELSE 'loss' END AS result
    FROM {{ source('worldcup', 'matches') }}
    WHERE group_name IS NOT NULL AND away_score IS NOT NULL
)

SELECT
    tm.tournament_id,
    tm.group_name,
    tm.team_id,
    t.team_name,
    COUNT(*) AS matches_played,
    SUM(CASE WHEN result = 'win' THEN 1 ELSE 0 END) AS wins,
    SUM(CASE WHEN result = 'draw' THEN 1 ELSE 0 END) AS draws,
    SUM(CASE WHEN result = 'loss' THEN 1 ELSE 0 END) AS losses,
    SUM(goals_for) AS goals_for,
    SUM(goals_against) AS goals_against,
    SUM(goals_for) - SUM(goals_against) AS goal_difference,
    SUM(CASE WHEN result = 'win' THEN 3 WHEN result = 'draw' THEN 1 ELSE 0 END) AS points,
    RANK() OVER (
        PARTITION BY tm.tournament_id, tm.group_name
        ORDER BY
            SUM(CASE WHEN result = 'win' THEN 3 WHEN result = 'draw' THEN 1 ELSE 0 END) DESC,
            SUM(goals_for) - SUM(goals_against) DESC,
            SUM(goals_for) DESC
    ) AS group_rank
FROM team_matches tm
JOIN {{ source('worldcup', 'teams') }} t ON t.team_id = tm.team_id
GROUP BY tm.tournament_id, tm.group_name, tm.team_id, t.team_name