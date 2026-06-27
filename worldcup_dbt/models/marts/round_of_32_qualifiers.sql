SELECT
    tournament_id, group_name, team_id, team_name,
    points, goal_difference, goals_for,
    'Automatic (Top 2)' AS qualification_route
FROM {{ ref('group_standings') }}
WHERE group_rank <= 2

UNION ALL

SELECT
    tournament_id, group_name, team_id, team_name,
    points, goal_difference, goals_for,
    'Best Third Place' AS qualification_route
FROM {{ ref('third_place_ranking') }}
WHERE third_place_rank <= {{ var('third_place_advance_count') }}