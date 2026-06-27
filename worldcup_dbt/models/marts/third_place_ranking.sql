SELECT
    *,
    RANK() OVER (
        PARTITION BY tournament_id
        ORDER BY points DESC, goal_difference DESC, goals_for DESC
    ) AS third_place_rank
FROM {{ ref('group_standings') }}
WHERE group_rank = 3