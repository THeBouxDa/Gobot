SELECT DISTINCT m.*
FROM moves m

LEFT JOIN character_aliases ca
    ON m.char_name = ca.char_name

LEFT JOIN move_aliases ma
    ON m.char_name = ma.char_name AND m.input = ma.move_input

WHERE
    (m.char_name = :char
    OR ca.alias = :char)

    AND

    (';' || m.input || ';' LIKE '%;' || :move || ';%'
    OR m.name = :move
    OR ma.alias = :move);