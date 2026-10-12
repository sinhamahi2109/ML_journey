SELECT COUNT(*) FROM matches;
SELECT COUNT(*) FROM DELIVERIES;
SELECT * FROM matches limit 10;
SELECT * FROM deliveries limit 10;

DESCRIBE matches;
describe deliveries;

SELECT DISTINCT team1 FROM matches ORDER BY team1;

UPDATE matches SET toss_winner='Delhi Capitals' WHERE toss_winner='Delhi Daredevils';
UPDATE matches SET winner='Delhi Capitals' WHERE winner='Delhi Daredevils';
UPDATE matches SET team1='Delhi Capitals' WHERE team1='Delhi Daredevils';
UPDATE matches SET team2='Delhi Capitals' WHERE team2='Delhi Daredevils';
UPDATE deliveries SET batting_team='Delhi Capitals' WHERE batting_team='Delhi Daredevils';
UPDATE deliveries SET bowling_team='Delhi Capitals' WHERE bowling_team='Delhi Daredevils';


UPDATE matches SET toss_winner='Gujarat Titans' WHERE toss_winner='Gujarat Lions';
UPDATE matches SET winner='Gujarat Titans' WHERE winner='Gujarat Lions';
UPDATE matches SET team1='Gujarat Titans' WHERE team1='Gujarat Lions';
UPDATE matches SET team2='Gujarat Titans' WHERE team2='Gujarat Lions';
UPDATE deliveries SET batting_team='Gujarat Titans' WHERE batting_team='Gujarat Lions';
UPDATE deliveries SET bowling_team='Gujarat Titans' WHERE bowling_team='Gujarat Lions';


UPDATE matches SET toss_winner='Punjab Kings' WHERE toss_winner='Kings XI Punjab';
UPDATE matches SET winner='Punjab Kings' WHERE winner='Kings XI Punjab';
UPDATE matches SET team1='Punjab Kings' WHERE team1='Kings XI Punjab';
UPDATE matches SET team2='Punjab Kings' WHERE team2='Kings XI Punjab';
UPDATE deliveries SET batting_team='Punjab Kings' WHERE batting_team='Kings XI Punjab';
UPDATE deliveries SET bowling_team='Punjab Kings' WHERE bowling_team='Kings XI Punjab';



UPDATE matches SET toss_winner='Rising Pune Supergiant' WHERE toss_winner='Rising Pune Supergiants';
UPDATE matches SET winner='Rising Pune Supergiant' WHERE winner='Rising Pune Supergiants';
UPDATE matches SET team1='Rising Pune Supergiant' WHERE team1='Rising Pune Supergiants';
UPDATE matches SET team2='Rising Pune Supergiant' WHERE team2='Rising Pune Supergiants';
UPDATE deliveries SET batting_team='Rising Pune Supergiant' WHERE batting_team='Rising Pune Supergiants';
UPDATE deliveries SET bowling_team='Rising Pune Supergiant' WHERE bowling_team='Rising Pune Supergiants';


UPDATE matches SET toss_winner='Royal Challengers Bangalore' WHERE toss_winner='Royal Challengers Bengaluru';
UPDATE matches SET winner='Royal Challengers Bangalore' WHERE winner='Royal Challengers Bengaluru';
UPDATE matches SET team1='Royal Challengers Bangalore' WHERE team1='Royal Challengers Bengaluru';
UPDATE matches SET team2='Royal Challengers Bangalore' WHERE team2='Royal Challengers Bengaluru';
UPDATE deliveries SET batting_team='Royal Challengers Bangalore' WHERE batting_team='Royal Challengers Bengaluru';
UPDATE deliveries SET bowling_team='Royal Challengers Bangalore' WHERE bowling_team='GRoyal Challengers Bengaluru';


UPDATE matches 
SET toss_winner = 'Gujarat Lions' 
WHERE toss_winner = 'Gujarat Titans' AND season IN (2016, 2017);

UPDATE matches 
SET winner = 'Gujarat Lions' 
WHERE winner = 'Gujarat Titans' AND season IN (2016, 2017);

UPDATE matches 
SET team1 = 'Gujarat Lions' 
WHERE team1 = 'Gujarat Titans' AND season IN (2016, 2017);

UPDATE matches 
SET team2 = 'Gujarat Lions' 
WHERE team2 = 'Gujarat Titans' AND season IN (2016, 2017);

UPDATE deliveries 
SET batting_team = 'Gujarat Lions' 
WHERE batting_team = 'Gujarat Titans' 
  AND match_id IN (
      SELECT id FROM matches WHERE season IN (2016, 2017)
  );

UPDATE deliveries 
SET bowling_team = 'Gujarat Lions' 
WHERE bowling_team = 'Gujarat Titans' 
  AND matchId IN (
      SELECT id FROM matches WHERE season IN (2016, 2017)
  );
  
  UPDATE deliveries 
SET batting_team = 'Gujarat Lions' 
WHERE batting_team = 'Gujarat Titans' 
  AND date < '2020-01-01';

UPDATE deliveries 
SET bowling_team = 'Gujarat Lions' 
WHERE bowling_team = 'Gujarat Titans' 
  AND date < '2020-01-01';