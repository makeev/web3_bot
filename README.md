# sanic skeleton with mongodb and minio

### dev

```
cd src
sanic app.app --access-log --dev
```

### prod
```
cd src
sanic app.app --no-access-logs --workers=4
```

## базовые env переменные

```
MONGO_URI="mongodb://localhost:27017"
MONGO_DB="dbname"
DEBUG=True
REDIS_URL="redis://127.0.0.1:6379/0"
```

---

## чтобы все работало надо еще прописать

```
ETH_HTTP_NODE_URL=https://something.quiknode.pro/<secret>
POLYGON_HTTP_NODE_URL=https://something.quiknode.pro/<secret>
```

это урлы нод для полигона и эфира соответственно, можно поднять свои или купить 
за $9 на quicknode.pro

---

```
ETHERSCAN_API_KEY='..'
POLYGONSCAN_API_KEY='...'
```

это ключи к scan api(etherscan.io, polygonscan.com), чтобы добывать подробности 
транзакций и abi контрактов например. 
Получить можно тут https://etherscan.io/myapikey

---

## запуск тасков

Есть просто реализованная manage команда, которая позволяет запускать все что 
есть в src/project/tasks.py

```
./manage.py parse_uniswap_tokens
```

Там же можно настроить таски на cron
