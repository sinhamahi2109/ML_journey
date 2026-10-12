SELECT*
FROM deliveries
limit 10;

-- 6. Who has hit the most sixes?
SELECT batsman, COUNT(*) as sixes
FROM deliveries
where batsman_runs=6
group by batsman
order by sixes desc
limit 10;


-- 7. Who has the best strike rate (at least 500 balls faced)?
SELECT batsman, 
       SUM(batsman_runs) AS runs,
       COUNT(*) AS balls,
       ROUND(100* SUM(batsman_runs)/COUNT(*),2) AS strike_rate
FROM deliveries
WHERE isWide IS NOT NULL or isWide=0
GROUP BY batsman
HAVING COUNT(*)>=500
ORDER BY 4 DESC
LIMIT 10;


-- 8. Who has taken the most wickets?
 SELECT bowler, COUNT(*) AS wickets
 FROM deliveries
 WHERE dismissal_kind IS NOT NULL AND 
       dismissal_kind <>'' AND
       dismissal_kind NOT IN ('run out', 'retired hurt', 'retired out', 'obstructing the field')
       
 GROUP BY bowler
 ORDER BY wickets desc
 LIMIT 10;
 
 
 -- 9. Which bowlers have bowled the most dot balls?
 SELECT bowler, COUNT(*) AS most_dot_balls
 FROM deliveries
 WHERE batsman_runs = 0 AND extras = 0
 GROUP BY bowler
 ORDER BY most_dot_balls desc
 LIMIT 10;