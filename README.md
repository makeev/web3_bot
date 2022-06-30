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

## env vars

```
MONGO_URI="mongodb://localhost:27017"
MONGO_DB="dbname"
DEBUG=True
REDIS_URL="redis://127.0.0.1:6379/0"
```

