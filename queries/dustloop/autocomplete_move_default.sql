SELECT DISTINCT m.name, m.char_name, m.input
FROM moves m

LEFT JOIN character_aliases ca
    ON m.char_name = ca.char_name

WHERE m.char_name = :char
OR ca.alias = :char

ORDER BY move_id ASC
LIMIT 25;