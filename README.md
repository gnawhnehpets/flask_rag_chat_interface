Build and run the docker container:

```
docker build -t flask-interface .
docker run -p 5000:5000 --env-file .env flask-interface
```

This will build your Docker image with the tag `flask-interface` and run it, making your application available at http://localhost:5000.

