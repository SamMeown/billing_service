# Очередь через rabbitMQ

1. Access
```bash
url: http://localhost:15672/#/
login: guest
passwd: guest
```

2You may encounter this error
```bash
ERROR: for rabbitmq  Cannot start service rabbitmq: driver failed programming external connectivity on endpoint rabbitmq_rabbitmq_1 (a62f4fe0d43ca3c86413eaa8903bc781bced540343a341cdc3be6711875daba8): Error starting userland proxy: listen tcp4 0.0.0.0:15672: bind: address already in use
```
command to help close the port
```bash
sudo lsof -i -P -n | grep <port number>  # List who's using the port
```

Материал:
- [Python + RabbitMQ][1]

[1]: https://www.rabbitmq.com/tutorials/tutorial-one-python.html