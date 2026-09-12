INSERT INTO character_aliases (alias, char_name)
SELECT :alias, name
FROM characters
WHERE name = :char