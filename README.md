## Инструментальные средства разработки ПО
## Практическое задание номер 2

### Установка

1. Клонируйте репозиторий
```
git clone https://github.com/n0tsSzzz/python-rmq-pubsub
```

2. Зайдите в папку с проектом и пропишите
```
cd python-rmq-pubsub
docker-compose up -d
```

3. Для проверки бд
```
docker exec -it python-rmq-pubsub-cassandra-1 cqlsh -e "USE pubsub; SELECT * FROM messages_1; SELECT * FROM messages_2;
```
