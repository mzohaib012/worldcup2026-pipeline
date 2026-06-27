SELECT
    p.player_id,
    p.full_name,
    COUNT(g.goal_id) AS total_goals
FROM {{ source('worldcup', 'players') }} p
JOIN {{ source('worldcup', 'match_goals') }} g
    ON p.player_id = g.player_id
GROUP BY p.player_id, p.full_name
ORDER BY total_goals DESC