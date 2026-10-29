SELECT count(*) AS row_count
FROM faker.generate_users('en_US', 'test-seed', 0, 10);


(
    SELECT * FROM faker.generate_users('de_DE', 'repeatable', 0, 10)
    EXCEPT
    SELECT * FROM faker.generate_users('de_DE', 'repeatable', 0, 10)
)
UNION ALL
(
    SELECT * FROM faker.generate_users('de_DE', 'repeatable', 0, 10)
    EXCEPT
    SELECT * FROM faker.generate_users('de_DE', 'repeatable', 0, 10)
);


SELECT
    bool_and(latitude BETWEEN -90 AND 90) AS valid_latitudes,
    bool_and(longitude >= -180 AND longitude < 180) AS valid_longitudes
FROM faker.generate_users('en_US', 'geo-test', 0, 100);


SELECT user_index
FROM faker.generate_users('en_US', 'batch-test', 1, 10)
ORDER BY user_index;


SELECT
    bool_and(height_cm BETWEEN 140 AND 210) AS valid_heights,
    bool_and(weight_kg BETWEEN 40 AND 150) AS valid_weights
FROM faker.generate_users('de_DE', 'physical-test', 0, 100);


SELECT value AS dictionary_version
FROM faker.meta
WHERE key = 'dictionary_version';
