-- 14: Run rate by phase of the innings
SELECT CASE WHEN `over` < 6 THEN '1 Powerplay (overs 1-6)'
            WHEN `over` < 15 THEN '2 Middle (overs 7-15)'
            ELSE '3 Death (overs 16-20)' END AS phase,
       SUM(batsman_runs + extras) AS runs,
       ROUND(6 * SUM(batsman_runs + extras) /
         SUM(CASE WHEN (isWide IS NULL OR isWide = 0) AND (isNoBall IS NULL OR isNoBall = 0) THEN 1 ELSE 0 END), 2) AS run_rate
FROM deliveries
GROUP BY phase
ORDER BY phase;

-- 15: Most wickets in the death overs
SELECT bowler, COUNT(*) AS death_wickets
FROM deliveries
WHERE `over` >= 15
  AND dismissal_kind IS NOT NULL AND dismissal_kind <> ''
  AND dismissal_kind NOT IN ('run out', 'retired hurt', 'retired out', 'obstructing the field')
GROUP BY bowler
ORDER BY death_wickets DESC
LIMIT 10;


-- 16: Mumbai Indians vs Chennai Super Kings, who has won more?
SELECT winner, COUNT(*) AS wins
FROM matches
WHERE ((team1 = 'Mumbai Indians' AND team2 = 'Chennai Super Kings')
    OR (team1 = 'Chennai Super Kings' AND team2 = 'Mumbai Indians'))
  AND winner IN ('Mumbai Indians', 'Chennai Super Kings')
GROUP BY winner;


-- 17: Head-to-head record for ALL team pairs
SELECT LEAST(team1, team2) AS team_a,
       GREATEST(team1, team2) AS team_b,
       COUNT(*) AS matches_played,
       SUM(CASE WHEN winner = LEAST(team1, team2) THEN 1 ELSE 0 END) AS team_a_wins,
       SUM(CASE WHEN winner = GREATEST(team1, team2) THEN 1 ELSE 0 END) AS team_b_wins,
       COUNT(*)
         - SUM(CASE WHEN winner = LEAST(team1, team2) THEN 1 ELSE 0 END)
         - SUM(CASE WHEN winner = GREATEST(team1, team2) THEN 1 ELSE 0 END) AS no_result
FROM matches
WHERE team1 IS NOT NULL AND team2 IS NOT NULL
GROUP BY team_a, team_b
ORDER BY matches_played DESC;


-- 18: Average first-innings score by venue (venues with 10+ matches)
SELECT m.venue,
       COUNT(*) AS matches,
       ROUND(AVG(s.runs), 1) AS avg_first_innings
FROM (SELECT matchId, SUM(batsman_runs + extras) AS runs
      FROM deliveries
      WHERE inning = 1
      GROUP BY matchId) AS s
JOIN matches m ON s.matchId = m.matchId
GROUP BY m.venue
HAVING COUNT(*) >= 10
ORDER BY avg_first_innings DESC
LIMIT 10;



-- 19: Win percentage per team (teams with 50+ matches)
SELECT t.team,
       COUNT(*) AS played,
       SUM(CASE WHEN t.team = m.winner THEN 1 ELSE 0 END) AS won,
       ROUND(100 * SUM(CASE WHEN t.team = m.winner THEN 1 ELSE 0 END) / COUNT(*), 1) AS win_pct
FROM (SELECT matchId, team1 AS team FROM matches
      UNION ALL
      SELECT matchId, team2 FROM matches) AS t
JOIN matches m ON t.matchId = m.matchId
GROUP BY t.team
HAVING COUNT(*) >= 50
ORDER BY win_pct DESC;


-- 20: Top 10 individual innings
SELECT d.batsman, m.season, SUM(d.batsman_runs) AS runs
FROM deliveries d
JOIN matches m ON d.matchId = m.matchId
GROUP BY d.matchId, d.batsman, m.season
ORDER BY runs DESC
LIMIT 10;