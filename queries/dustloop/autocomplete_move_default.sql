SELECT input FROM moves
WHERE char_name = :char
ORDER BY move_id ASC
LIMIT 25;