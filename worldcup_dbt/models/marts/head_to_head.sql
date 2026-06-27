SELECT
    LEAST(home_team_id, away_team_id) AS team_a_id,
    GREATEST(home_team_id, away_team_id) AS team_b_id,
    ta.team_name AS team_a_name,
    tb.team_name AS team_b_name,
    COUNT(*) AS matches_played,
    SUM(CASE
        WHEN home_team_id = LEAST(home_team_id, away_team_id) AND home_score > away_score THEN 1
        WHEN away_team_id = LEAST(home_team_id, away_team_id) AND away_score > home_score THEN 1
        ELSE 0
    END) AS team_a_wins,
    SUM(CASE
        WHEN home_team_id = GREATEST(home_team_id, away_team_id) AND home_score > away_score THEN 1
        WHEN away_team_id = GREATEST(home_team_id, away_team_id) AND away_score > home_score THEN 1
        ELSE 0
    END) AS team_b_wins,
    SUM(CASE WHEN home_score = away_score THEN 1 ELSE 0 END) AS draws
FROM {{ source('worldcup', 'matches') }} m
JOIN {{ source('worldcup', 'teams') }} ta ON ta.team_id = LEAST(home_team_id, away_team_id)
JOIN {{ source('worldcup', 'teams') }} tb ON tb.team_id = GREATEST(home_team_id, away_team_id)
WHERE home_score IS NOT NULL
GROUP BY LEAST(home_team_id, away_team_id), GREATEST(home_team_id, away_team_id), ta.team_name, tb.team_name
ORDER BY matches_played DESC