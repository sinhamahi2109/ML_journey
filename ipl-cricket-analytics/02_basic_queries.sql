-- 1.  How many matches were played each season?
SELECT *
FROM matches LIMIT 10;


SELECT *
FROM deliveries LIMIT 10;


SELECT season , COUNT(*) AS total_matches
FROM matches
GROUP BY season
ORDER BY season;


-- 2. Which team won most matches?
SELECT winner , COUNT(*) AS most_win
FROM matches
WHERE winner IS NOT NULL AND winner <>''
GROUP BY winner
ORDER BY 2 DESC;


-- 3. Does winning the toss help win the match as well?
SELECT COUNT(*) AS total_matches,
SUM(CASE 
    WHEN toss_winner=winner THEN 1 ELSE 0 END
    )AS toss_winner_won,
ROUND(100*(SUM(CASE 
    WHEN toss_winner=winner THEN 1 ELSE 0 END
    ))/COUNT(*),1 )AS percent
FROM matches
WHERE (winner IS NOT NULL and winner<>'') AND (toss_winner IS NOT NULL and toss_winner<>'');



-- 4. Which 10 Venue hosted the most matches?
SELECT venue, Count(*) AS match_hosted
FROM matches
WHERE venue IS NOT NULL AND venue<>''
group by venue
ORDER by 2 desc
LIMIT 10;

SELECT DISTINCT venue 
FROM matches
WHERE venue IS NOT NULL AND venue<>''
;

UPDATE matches
SET venue = CASE
    -- Bengaluru
    WHEN venue IN ('M Chinnaswamy Stadium', 'M.Chinnaswamy Stadium') 
      THEN 'M Chinnaswamy Stadium, Bengaluru'
    
    -- Delhi (Renamed from Feroz Shah Kotla)
    WHEN venue IN ('Feroz Shah Kotla', 'Arun Jaitley Stadium') 
      THEN 'Arun Jaitley Stadium, Delhi'
    
    -- Mohali
    WHEN venue IN ('Punjab Cricket Association Stadium, Mohali', 
                   'Punjab Cricket Association IS Bindra Stadium', 
                   'Punjab Cricket Association IS Bindra Stadium, Mohali', 
                   'Punjab Cricket Association IS Bindra Stadium, Mohali, Chandigarh') 
      THEN 'Punjab Cricket Association IS Bindra Stadium, Mohali'
    
    -- Chennai
    WHEN venue IN ('MA Chidambaram Stadium', 'MA Chidambaram Stadium, Chepauk, Chennai') 
      THEN 'MA Chidambaram Stadium, Chepauk'
    
    -- Hyderabad
    WHEN venue IN ('Rajiv Gandhi International Stadium', 'Rajiv Gandhi International Stadium, Uppal, Hyderabad') 
      THEN 'Rajiv Gandhi International Stadium, Uppal'
    
    -- Ahmedabad (Renamed from Motera)
    WHEN venue = 'Sardar Patel Stadium, Motera' 
      THEN 'Narendra Modi Stadium, Ahmedabad'
    
    -- Mumbai
    WHEN venue = 'Wankhede Stadium' 
      THEN 'Wankhede Stadium, Mumbai'
    WHEN venue = 'Brabourne Stadium' 
      THEN 'Brabourne Stadium, Mumbai'
    WHEN venue = 'Dr DY Patil Sports Academy' 
      THEN 'Dr DY Patil Sports Academy, Mumbai'
    
    -- Pune (Renamed from Subrata Roy Sahara)
    WHEN venue IN ('Subrata Roy Sahara Stadium', 'Maharashtra Cricket Association Stadium') 
      THEN 'Maharashtra Cricket Association Stadium, Pune'
    
    -- Kolkata & Jaipur
    WHEN venue = 'Eden Gardens' 
      THEN 'Eden Gardens, Kolkata'
    WHEN venue = 'Sawai Mansingh Stadium' 
      THEN 'Sawai Mansingh Stadium, Jaipur'
    
    -- Dharamsala
    WHEN venue = 'Himachal Pradesh Cricket Association Stadium' 
      THEN 'Himachal Pradesh Cricket Association Stadium, Dharamsala'
    
    -- Visakhapatnam
    WHEN venue = 'Dr. Y.S. Rajasekhara Reddy ACA-VDCA Cricket Stadium, Visakhapatnam' 
      THEN 'Dr. Y.S. Rajasekhara Reddy ACA-VDCA Cricket Stadium'
    
    -- Abu Dhabi
    WHEN venue = 'Sheikh Zayed Stadium' 
      THEN 'Zayed Cricket Stadium, Abu Dhabi'
    
    ELSE venue
END;



-- 5. Top 10 run scorers of all time?
SELECT batsman, SUM(batsman_runs) AS total_runs_by_batsman
FROM deliveries
WHERE batsman_runs IS NOT NULL 
group by batsman
order by 2 desc
limit 10;