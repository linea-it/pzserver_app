

## Develop Enviroment

Faça o clone do repositório e acesse o diretório.

```bash
git clone https://github.com/linea-it/pz-server.git pzserver
cd pzserver
```

Copie o arquivo `docker-compose-development.yml` e renomeie para `docker-compose.yml`

```bash
cp docker-compose-development.yml docker-compose.yml
```

### Setup Database

Inicie o serviço do banco de dados e espere a mensagem `database system is ready to accept connections` para só depois iniciar o backend.

```bash
docker-compose up database
```

### Setup Frontend
Antes de iniciar o container do frontend é necessário instalar as dependencias do react.
```bash
docker-compose run frontend yarn
```
