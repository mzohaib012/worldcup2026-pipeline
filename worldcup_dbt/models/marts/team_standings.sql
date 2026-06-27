WITH team_matches AS (
    SELECT
        home_team_id AS team_id,
        home_score AS goals_for,
        away_score AS goals_against,
        CASE
            WHEN home_score > away_score THEN 'win'
            WHEN home_score = away_score THEN 'draw'
            ELSE 'loss'
        END AS result
    FROM {{ source('worldcup', 'matches') }}
    WHERE home_score IS NOT NULL

    UNION ALL

    SELECT
        away_team_id AS team_id,
        away_score AS goals_for,
        home_score AS goals_against,
        CASE
            WHEN away_score > home_score THEN 'win'
            WHEN away_score = home_score THEN 'draw'
            ELSE 'loss'
        END AS result
    FROM {{ source('worldcup', 'matches') }}
    WHERE away_score IS NOT NULL
)

SELECT
    t.team_id,
    t.team_name,
    COUNT(*) AS matches_played,
    SUM(CASE WHEN tm.result = 'win' THEN 1 ELSE 0 END) AS wins,
    SUM(CASE WHEN tm.result = 'draw' THEN 1 ELSE 0 END) AS draws,
    SUM(CASE WHEN tm.result = 'loss' THEN 1 ELSE 0 END) AS losses,
    SUM(tm.goals_for) AS goals_for,
    SUM(tm.goals_against) AS goals_against,
    SUM(tm.goals_for) - SUM(tm.goals_against) AS goal_difference,
    (SUM(CASE WHEN tm.result = 'win' THEN 3 WHEN tm.result = 'draw' THEN 1 ELSE 0 END)) AS points
FROM team_matches tm
JOIN {{ source('worldcup', 'teams') }} t
    ON tm.team_id = t.team_id
GROUP BY t.team_id, t.team_name
ORDER BY points DESC, goal_difference DESC