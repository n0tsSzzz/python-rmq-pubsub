## Инструментальные средства разработки ПО
## Практическое задание номер 2

### Установка

1. Клонируйте репозиторий
```
https://github.com/n0tsSzzz/python-rmq-pubsub
```

2. Зайдите в папку с проектом и пропишите
```
cd python-rmq-pubsub
docker-compose up -d
```

3. Для проверки бд
```
docker exec -it software_prac-cassandra-1 cqlsh -e "USE pubsub; SELECT * FROM messages_1; SELECT * FROM messages_2;"
```
