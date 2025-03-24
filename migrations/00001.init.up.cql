CREATE KEYSPACE IF NOT EXISTS pubsub
WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

USE pubsub;

CREATE TABLE IF NOT EXISTS messages_1 (
    id timeuuid PRIMARY KEY,
    content text
);

CREATE TABLE IF NOT EXISTS messages_2 (
    id timeuuid PRIMARY KEY,
    content text
);