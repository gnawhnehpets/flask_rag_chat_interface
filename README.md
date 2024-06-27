First, build image:

```
docker build -t flask-interface .
docker run -p 5000:5000 --env-file .env flask-interface
```