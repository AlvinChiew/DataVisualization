-- Q5 List of driver ID who took orders, but never complete an order?
SELECT servicer_auth
FROM lalamovebiengineeringtest.vaninterest
WHERE idvanOrder IN (
	SELECT idvanOrder
	FROM lalamovebiengineeringtest.vanorder
	WHERE order_status <> 2
)
AND servicer_auth NOT IN (
	SELECT servicer_auth 
	FROM lalamovebiengineeringtest.vanorder
	WHERE order_status = 2
)
;

-- Q4 4) List of all drivers who took order(s) (regardless of whether they eventually complete the order), 
-- also show each driver's total income and total order(s) completed. 
-- Order the list by total income (descending), then by total order(s) completed
SELECT 
b.servicer_auth
,CASE 
	WHEN a.total_income IS NULL THEN 0
    ELSE a.total_income
    END AS 'total_income'
,CASE 
	WHEN a.total_order IS NULL THEN 0
    ELSE a.total_order
    END AS 'total_order'
 FROM (
	SELECT 
	servicer_auth
	,SUM(total_price) AS 'total_income'
	,COUNT(idvanOrder) AS 'total_order'
	FROM lalamovebiengineeringtest.vanorder
	WHERE order_status = 2
	GROUP BY servicer_auth
) AS a
RIGHT JOIN (
	SELECT DISTINCT servicer_auth
	FROM lalamovebiengineeringtest.vaninterest
    UNION
 	SELECT DISTINCT servicer_auth
	FROM lalamovebiengineeringtest.vanorder   
    -- WHERE servicer_auth IS NOT NULL
) AS b ON (a.servicer_auth = b.servicer_auth)
;

-- Q3 3) List of unique Client ID who completed at least one order, 
-- also show each client's total money spent, and the total order(s) completed. 
-- Order the list by total money spent (descending), then by total order(s) completed (descending) --
SELECT requestor_client_id, SUM(total_price) AS 'total_payment', COUNT(idvanOrder) AS 'total_order'
FROM lalamovebiengineeringtest.vanorder
WHERE order_status = 2
GROUP BY requestor_client_id
ORDER BY total_payment DESC, total_order DESC
;

-- Q2 What is the percentage of money spent for each of the following group of clients? --
-- Clients who completed 1 order
-- Clients who completed more than 1 order --
SELECT 
client_group
,SUM(total_price) AS 'total_price'
,SUM(total_price) / b.total_revenue * 100 AS '%_total_price'
FROM(
	SELECT requestor_client_id
    -- , COUNT(idvanOrder) AS '#_order'
    ,CASE 
		WHEN COUNT(idvanOrder) = 1 THEN 'Clients who completed 1 order'
		ELSE 'Clients who completed more than 1 order'
		END AS 'client_group'
    ,  SUM(total_price) AS 'total_price'
	FROM lalamovebiengineeringtest.vanorder
	WHERE order_status = 2
	GROUP BY  requestor_client_id
) AS a
CROSS JOIN (
	SELECT SUM(total_price) AS 'total_revenue' 
    FROM lalamovebiengineeringtest.vanorder
    WHERE order_status = 2
) AS b
GROUP BY client_group
;

-- Q1 For hours with orders, how many orders are there each hour based on order time? --
SELECT DATE_FORMAT(order_datetime, '%Y-%m-%d  %H H') AS 'order_dateHour', COUNT(idvanOrder) AS '# order'
FROM lalamovebiengineeringtest.vanorder
GROUP BY order_dateHour
ORDER BY order_dateHour;

-- TEST --
SELECT * FROM lalamovebiengineeringtest.vaninterest
WHERE txCreate > '2017-04-18 23:00:00';
SELECT * FROM lalamovebiengineeringtest.vanorder;
SELECT * FROM lalamovebiengineeringtest.vaninterest LIMIT 1;
SELECT * FROM lalamovebiengineeringtest.vaninterest
-- WHERE DATE_FORMAT(txCreate , '%Y-%m-%d %H:%i:%s') > '2017-04-18 23:00:00';
WHERE STR_TO_DATE(txCreate , '%m/%d/%Y %H:%i') > '2017-04-18 23:00:00';