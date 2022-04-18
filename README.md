
## Setup Develop Enviroment

Faça o clone do repositório e acesse o diretório.

```bash
git clone https://github.com/linea-it/pz-server.git pzserver
cd pzserver
```

Copie o arquivo `docker-compose-development.yml` e renomeie para `docker-compose.yml`

```bash
cp docker-compose-development.yml docker-compose.yml
```

Crie o arquivo de variaveis de ambiente baseado no `env_template`.

```bash
cp env_template .env
```

Edite o arquivo e altere as variaveis de acordo com seu ambiente, neste primeiro momento de anteção as variaveis referentes ao banco de dados e de conexão do django.

Agora inicie o serviço de banco de dados, é importante que a primeira vez o serviço do banco de dados seja ligado sozinho, nesta etapa o postgresql vai criar o banco de dados e o usuario baseado nas settings `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`.

```bash
docker-compose up database
```

Aguarde a mensagem `database system is ready to accept connections` e depois encerre o serviço com as teclas `CTRL + C` ou `docker-compose stop database` em outro terminal.

Agora inicie o serviço do backend, como é a primeira vez, vai ser feito o pull da imagem base e o build do container, isso pode demorar um pouco. Se tudo ocorrer normalmente a ultima mensagem será algo como `Booting worker with pid...`.

```bash
docker-compose up backend
```

Encerre o serviço do backend, para alterar uma das variaveis do Django.

Para encerrar utilize `CTRL + C` ou `docker-compose stop`.

Com os serviços desligados vamos executar um comando no container do backend para gerar uma SECRET para o Django.

```bash
docker-compose run backend python -c "import secrets; print(secrets.token_urlsafe())"
```

Está é a saída do comando:

```bash
$ docker-compose run backend python -c "import secrets; print(secrets.token_urlsafe())"
Creating pzserver_backend_run ... done
6klbHhaeA6J2imKt9AVVgS5yl9mCWoiQqrfUV469DLA
```

Copie a chave gerada e subistitua o valor da variavel `SECRET` no arquivo `.env`.

Agora crie o super úsuario do Django.

```bash
docker-compose run backend python manage.py createsuperuser
```

Agora instale as dependencias do Frontend executando o comando `yarn`. Por ser a primeira vez inciando este container, será feito o pull da imagem base o que pode demorar um pouco.

No ambiente de desenvolvimento não é necessário alterar as configurações do Ngnix.
Mas caso seja necessário uma alteração local, copie o arquivo `nginx_development.conf` para `nginx.conf`
Altere também o arquivo `docker-compose.yml` no serviço ngnix na linha `- ./nginx_development.conf:/etc/nginx/conf.d/default.conf:ro`. Desta forma o arquivo ngnix.conf representa seu ambiente local, caso faça alguma modificação que seja necessária para o projeto, copie esta modificação para o arquivo de template, pois o arquivo nginx.conf não faz parte do repositório.  

```bash
docker-compose run frontend yarn
```

Este comando vai criar o diretório `pzserver/frontend/node_modules` caso tenha algum problema com dependencias remova este diretório e execute o comando novamente.

Feito isto o processo de setup do ambiente de desenvolvimento está completo.

### Algus comandos de exemplo

Ligar o ambiente em background.

```bash
docker-compose up -d
```

Acesse no navegador:

- Frontend: <http://localhost/>
- Django Admin: <http://localhost/admin/>
- Django REST: <http://localhost/api>

Desligar todo ambiente

```bash
docker-compose stop
```

Restartar todo ambiente

```bash
docker-compose stop && docker-compose up -d
```

Executar um terminar em um dos serviços

```bash
# Com o serviço ligado
docker-compose exec backend bash
# Com o serviço desligado
docker-compose run backend bash
```

Acessar banco de dados com Psql

```bash
# Usar as credenciais que estão no .env
docker-compose exec database psql -h localhost -U <username> -d <database>
```

### Build manual das imagens e push para docker hub

Docker Hub: <https://hub.docker.com/repository/docker/linea/pzserver/>

No docker hub é apenas um repositório `linea/pzserver` e as imagens estão divididas em duas tags uma para o backend (**:backend_[version]**) e outra para frontend (**:frontend_[version]**). A identificação unica de cada tag pode ser o numero de versão exemplo: `linea/pzserver:backend_v0.1` ou a hash do commit para versões de desenvolvimento: `linea/pzserver:backend_8816330` para obter o hash do commit usar o comando `$(git describe --always)`.

**Importante:** Sempre fazer o build das duas imagens utilizando a mesma versão ou mesmo hash de commit, mesmo que uma das imagens não tenha sido alterada.

```bash
# Backend
cd pzserver/backend
docker build -t linea/pzserver:backend_$(git describe --always) .
# Para o push copie o nome da imagem que aparece no final do build e faça o docker push 
docker push linea/pzserver:backend_<commit_hash>

# Frontend
cd pzserver/frontend
docker build -t linea/pzserver:frontend_$(git describe --always) .
# Para o push copie o nome da imagem que aparece no final do build e faça o docker push 
docker push linea/pzserver:frontend_<commit_hash>
```

## Setup Production Enviroment

No ambiente de produção é necessário fazer clone do repositório.

O exemplo a seguir considera uma instalação onde o banco de dados e ngnix estão em containers como no ambiente de dev e os volumes são diretórios dentro da raiz pzserver.

Apenas:

- crie as pastas
- crie o arquivo docker-compose.yml
- crie o arquivo .env
- crie o arquivo ngnix.conf

Crie os diretórios `pzserver` e `archive`

```bash
mkdir pzserver pzserver/archive pzserver/archive/data pzserver/archive/django_static
cd pzserver
```

Crie um arquivo `docker-compose.yml` baseado no template `docker-compose-production.yml`
Edite o arquivo conforme as necessidades do ambiente.
Geralmente as mudanças são nos volumes e na porta do ngnix.

Crie um arquivo `.env` baseado no arquivo `env_template` edite as variaveis de acesso ao banco de dados.

Aguarde a mensagem `database system is ready to accept connections` e depois encerre o serviço com as teclas `CTRL + C` ou `docker-compose stop database` em outro terminal.

```bash
docker-compose up database
```

Inicie o serviço do backend aguarde a mensagem `Booting worker with pid...`.

```bash
docker-compose up backend
```

Encerre o serviço do backend e altere as variaveis do Django.
Edite o arquivo `.env`

Em produção é OBRIGATÓRIO desligar o Debug `DEBUG=0`. e alterar a variavel `SECRET` que deve ser unica para cada ambiente.

Com o serviço desligado execute o comando abaixo para gerar uma SECRET, copie e cole no .env

```bash
docker-compose run backend python -c "import secrets; print(secrets.token_urlsafe())"
```

Crie o arquivo de configuração do Ngnix `nginx.conf` baseado no arquivo `nginx_production.conf`


