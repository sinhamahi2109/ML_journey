ALTER TABLE matches MODIFY matchId INT;
ALTER TABLE deliveries MODIFY matchId INT;
CREATE INDEX idx_matches_matchid ON matches (matchId);
CREATE INDEX idx_deliveries_matchid ON deliveries (matchId);


-- 10. Runs scored and average runs per match in each season
SELECT m.season,
       COUNT(DISTINCT d.matchId)AS matches,
       SUM(d.batsman_runs+extras) AS total_runs,
       ROUND(SUM(d.batsman_runs+extras)/COUNT(DISTINCT d.matchId))AS runs_per_match
FROM deliveries d
JOIN matches m ON d.matchId=m.matchId
GROUP BY m.season
ORDER BY m.season;     



-- 11: Wins when batting first vs chasing
SELECT
  SUM(CASE WHEN winner = batting_first THEN 1 ELSE 0 END) AS won_batting_first,
  SUM(CASE WHEN winner <> batting_first THEN 1 ELSE 0 END) AS won_chasing,
  ROUND(100 * SUM(CASE WHEN winner = batting_first THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_won_batting_first,
  ROUND(100 * SUM(CASE WHEN winner<> batting_first THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_won_chasing
FROM (
  SELECT winner,
         CASE WHEN toss_decision = 'bat' THEN toss_winner
              WHEN toss_winner = team1 THEN team2
              ELSE team1 END AS batting_first
  FROM matches
  WHERE winner IS NOT NULL AND winner <> ''
) AS t;  



-- 12: Top run scorer of every season
WITH season_runs AS (
  SELECT m.season, d.batsman, SUM(d.batsman_runs) AS runs
  FROM deliveries d
  JOIN matches m ON d.matchId = m.matchId
  GROUP BY m.season, d.batsman
),
ranked AS (
  SELECT season, batsman, runs,
         RANK() OVER (PARTITION BY season ORDER BY runs DESC) AS rnk
  FROM season_runs
)
SELECT season, batsman, runs
FROM ranked
WHERE rnk = 1
ORDER BY season;


-- 13: Most Player of the Match awards
SELECT player_of_match, COUNT(*) AS awards
FROM matches
WHERE player_of_match IS NOT NULL AND player_of_match <> ''
GROUP BY player_of_match
ORDER BY awards DESC
LIMIT 10;