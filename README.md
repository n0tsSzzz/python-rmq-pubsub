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

3. Для проверки редиса
```
docker-compose exec redis redis-cli KEYS "msg:*"
```

4. Для проверки бд
```
docker exec -it python-rmq-pubsub-cassandra-1 cqlsh -e "USE pubsub; SELECT * FROM messages_1; SELECT * FROM messages_2;"
```

## Redis

- В редисе хранится ключ в виде msg:\<hash>, а в значение находися строка, которую считали
- Повторной обработки нет, потому что результат кэшируется в редисе
- TTL установлен на 24 часа
- Проблема гонки решена с помощью aioredlock