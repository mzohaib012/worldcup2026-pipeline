SELECT
    m.match_id,
    m.tournament_id,
    m.stage,
    m.match_date,
    th.team_name AS home_team,
    ta.team_name AS away_team,
    m.home_score,
    m.away_score,
    CASE
        WHEN m.home_score IS NULL OR m.away_score IS NULL THEN NULL
        WHEN m.home_score > m.away_score THEN th.team_name
        WHEN m.away_score > m.home_score THEN ta.team_name
        ELSE NULL
    END AS winner
FROM {{ source('worldcup', 'matches') }} m
LEFT JOIN {{ source('worldcup', 'teams') }} th ON th.team_id = m.home_team_id
LEFT JOIN {{ source('worldcup', 'teams') }} ta ON ta.team_id = m.away_team_id
WHERE m.stage IS NOT NULL
  AND m.stage != 'GROUP_STAGE'
ORDER BY
    CASE m.stage
        WHEN 'LAST_32' THEN 1
        WHEN 'LAST_16' THEN 2
        WHEN 'QUARTER_FINALS' THEN 3
        WHEN 'SEMI_FINALS' THEN 4
        WHEN 'THIRD_PLACE' THEN 5
        WHEN 'FINAL' THEN 6
        ELSE 99
    END,
    m.match_date