/* It seems that the parser for VSC thinks that some statements are faulty, such
as the following one. However it executes properly with sqlite3. */

/* how many good and bad based on number of people */
DROP TABLE IF EXISTS player_alignment;
DROP TABLE IF EXISTS people_per_quest;
DROP TABLE IF EXISTS required_fails_per_quest;

CREATE TABLE player_alignment AS
    SELECT 5 AS num_players, 3 AS num_good, 2 AS num_evil UNION
    SELECT 6, 4, 2 UNION
    SELECT 7, 4, 3 UNION
    SELECT 8, 5, 3 UNION
    SELECT 9, 6, 3 UNION
    SELECT 10, 6, 4;

/* how many people on each quest based on number of people */
CREATE TABLE people_per_quest AS
    SELECT 5 as num_players, 2 as quest_1, 3 as quest_2, 2 as quest_3, 3 as quest_4, 3 as quest_5 UNION
    SELECT 6, 2, 3, 4, 3, 4 UNION
    SELECT 7, 2, 3, 3, 4, 4 UNION
    SELECT 8, 3, 4, 4, 5, 5 UNION
    SELECT 9, 3, 4, 4, 5, 5 UNION
    SELECT 10, 3, 4, 4, 5, 5;

CREATE TABLE required_fails_per_quest AS
    SELECT 5 as num_players, 1 as quest_1, 1 as quest_2, 1 as quest_3, 1 as quest_4, 1 as quest_5 UNION
    SELECT 6, 1, 1, 1, 1, 1 UNION
    SELECT 7, 1, 1, 1, 2, 1 UNION
    SELECT 8, 1, 1, 1, 2, 1 UNION
    SELECT 9, 1, 1, 1, 2, 1 UNION
    SELECT 10, 1, 1, 1, 2, 1;


