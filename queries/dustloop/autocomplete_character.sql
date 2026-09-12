SELECT name FROM characters
WHERE name LIKE '%' || :cur || '%'
ORDER BY name ASC
LIMIT 25;