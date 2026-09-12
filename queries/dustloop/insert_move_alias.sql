INSERT INTO move_aliases (alias, move_input, char_name)
SELECT :alias, input, char_name
FROM moves
WHERE ';' || input || ';' LIKE '%;' || :move || ';%'
AND char_name = :char;