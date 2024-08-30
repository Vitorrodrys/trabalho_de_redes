
# Trabalho Redes

Este trabalho visou a transmissão de vídeos utilizando sockets UDP, fazendo o controle de bufferização.

## Requisitos

#### -Python 3.11
#### -Docker
#### -Docker Compose 2.29

## Funcionalidades

- Transmissão de vídeo
- Stop
- Pause
- Seek Forward
- Seek Backward
- Seek (para algum momento do vídeo)


## Como utilizar

### Clone o repositório

```bash
  gh repo clone Vitorrodrys/trabalho_de_redes
  cd trabalho_de_redes
```

### Inicie o servidor utilizando o docker

```bash
  cd server
  cd docker_configs
  docker compose up
```

Espere o docker finalizar as configurações

### Inicie o cliente usando o arquivo shell script

Vá para a pasta raiz

```bash
  cd client
  ./compila_e_executa.sh
```

### Peça o vídeo que deseja receber do servidor

Neste momento o cliente irá realizar a conexão e enviar através do canal TCP a porta UDP que ele irá utilizar, e o vídeo que você deseja.

Ex: (suponhamos que no servidor esteja o video "sintel_720.mkv")

```bash
  videos_volume/sintel_720.mkv
```

## Comandos disponíveis

Pausa e retoma a transmissão:
```bash
  pause
```

Finaliza a transmissão:
```bash
  quit
```

Avança a transmissão em 1%:
```bash
  seek_forward
```

Retarda a transimssão em 1%:
```bash
  seek_backward
```

Pula ou retoma a transmissão em um offset personalizado (em porcentagem):
```bash
  seek
  {insira o offset que deseja, em porcentagem}
```
    
## Autores

- [@Vitorrodrys](https://github.com/Vitorrodrys)
- [@H1gor1](https://github.com/H1gor1)
