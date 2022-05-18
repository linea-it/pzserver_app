# PhotoZ Server

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

Crie o arquivo de variáveis de ambiente baseado no `env_template`.

```bash
cp env_template .env
```

Edite o arquivo e altere as variáveis de acordo com seu ambiente, neste primeiro momento de atenção as variáveis referentes ao banco de dados e de conexão do django.

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

Crie o super úsuario do Django.

```bash
docker-compose run backend python manage.py createsuperuser
```

Importe os dados iniciais da aplicação utilizando o seguinte comando:

```bash
docker-compose run backend python manage.py loaddata initial_data
```

Este comando `loaddata` vai inserir no banco de dados algums registros basicos para o funcionamento da aplicação. estes registros estão no arquivo `core/fixtures/initial_data.yaml`.

Agora instale as dependencias do Frontend executando o comando `yarn`. Por ser a primeira vez inciando este container, será feito o pull da imagem base o que pode demorar um pouco.

```bash
docker-compose run frontend yarn
```

Este comando vai criar o diretório `pzserver/frontend/node_modules` caso tenha algum problema com dependencias remova este diretório e execute o comando novamente.

No ambiente de desenvolvimento não é necessário alterar as configurações do Ngnix.
Mas caso seja necessário uma alteração local, copie o arquivo `nginx_development.conf` para `nginx.conf`
Altere também o arquivo `docker-compose.yml` no serviço ngnix na linha `- ./nginx_development.conf:/etc/nginx/conf.d/default.conf:ro`. Desta forma o arquivo ngnix.conf representa seu ambiente local, caso faça alguma modificação que seja necessária para o projeto, copie esta modificação para o arquivo de template, pois o arquivo nginx.conf não faz parte do repositório.  

Feito isto o processo de setup do ambiente de desenvolvimento está completo.

**Recomendação:** Antes de realizar o push, é recomendável fazer o build do frontend para evitar que erros com o ESlint atrapalhe o processo de Pull Request:

``` bash
docker-compose run frontend yarn build
```

### Alguns comandos de exemplo

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

Adicionar Bibliotecas ao frontend utilizando yarn

``` bash
docker-compose run frontend yarn add <library>
```

### Adicionar autenticação OAuth com Github

#### Criando app OAuth no Github
Primeiramente devemos criar um app OAuth com uma conta Github. Segue link com o passo a passo:
- <https://docs.github.com/pt/developers/apps/building-oauth-apps/creating-an-oauth-app>

**Importante:**
- A Homepage URL deverá corresponder ao seguinte padrão: `http://<URL app>/api`
- A Authorization callback URL deverá corresponder ao seguinte padrão: `http://<URL app>/auth/complete/github-org/` 

Exemplo de URLs para ambiente de desenvolvimento:
- Homepage URL: `http://localhost/api`
- Authorization callback URL: `http://localhost/auth/complete/github-org/`

Após a criação, o aplicativo fornecerá um `CLIENT ID` e você deverá gerar um `CLIENT SECRET` na página de configuração da app. Essas informações deverão ser adicionadas ao `.env` do projeto nos respectivos campos:
``` bash
GITHUB_CLIENT_ID=<your CLIENT ID>
GITHUB_CLIENT_SECRET=<your CLIENT SECRET>
```
#### Configurando um aplicativo de OAuth interno
Vá para Django Admin e adicione um novo aplicativo com a seguinte configuração:

- `client_id` e `client_secret` devem ser deixados inalterados
- O `user` deve ser seu superusuário
- `redirect_uris` deve ser o mesmo endereço da Authorization callback URL
- `client_type` deve ser definido como `confidencial`
- `authorization_grant_type` deve ser definido como 'Authorization Code'
- `name` pode ser definido para o que você gostaria, sugestão: `Github`

A instalação é concluída, você pode agora testar o aplicativo recém-configurado.

OBS: Você pode adicionar outros aplicativos internos para fornecer tokens para os usuários criados diretamente no banco de dados, ou para se autenticar a outro provedor de OAuth como o do Facebook ou Google por exemplo.

#### Login com Github
Para se logar com o Github:
- Acesse a URL: `http://<URL app>/auth/login/github-org/`, você será redirecionado para se autenticar com suas credenciais do Github. 
- Após se logar, dê permissão ao app de vizualizar a organização linea-it.
- Você será redirecionado ao endereço: `http://<URL app>/api`

Pronto você esta logado na aplicação com sua conta Github. O próximo passo é converter o código de acesso do Github a um token interno.

#### Converter user access code em token interno
- Acesse o Django admin e visualize o registro criado na tabela `User social auths` referente ao seu usuário. 
- Recupere o user access code (access_token) diretamente no registro
- Use o seguinte comando para converter seu código Github em um token interno, substituindo `URL app`, `client_id`, `client_secret` e o `user_access_token`:
``` bash
curl -X POST -d "grant_type=convert_token&client_id=<django-oauth-generated-client_id>&client_secret=<django-oauth-generated-client_secret>&backend=github-org&token=<user_access_token>" http://<URL app>/auth/convert-token
```

Essa solicitação retorna um "access_token" que você deve usar com todas as solicitações HTTP para sua API REST. O que está acontecendo aqui é que estamos convertendo um token de acesso de terceiros (<user_access_token>) em um token de acesso para usar com sua API e seus clientes ("access_token"). Você deve usar esse token em todas as comunicações futuras entre seu sistema/aplicativo e sua API para autenticar cada solicitação e evitar sempre a autenticação com o Github.

Exemplos:
- Para acessar o endpoint que lista todos releases:
    ``` bash
    curl -H "Authorization: Bearer <access_token>" http://<URL app>/api/releases/
    ```
- Refresh token:
    ``` bash
    curl -X POST -d "grant_type=refresh_token&client_id=<django-oauth-generated-client_id>&client_secret=<django-oauth-generated-client_secret>&refresh_token=<your_refresh_token>" http://<URL app>/auth/token
    ```
- Revoke a single token:
    ``` bash
    curl -X POST -d "client_id=<django-oauth-generated-client_id>&client_secret=<django-oauth-generated-client_secret>&token=<access_token>" http://<URL app>/auth/revoke-token
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

No ambiente de produção **Não** é necessário fazer clone do repositório.

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

Altere as imagens do frontend e backend para a versão desejada, substitua a string `<VERSION>` pela tag da imagem.

Altere a porta que será utilizada para a aplicação, substitua a string `<PORT>` por uma porta que esteja disponivel no ambiente, está porta é que deverá ser associada a url da aplicação.

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

Em produção é **OBRIGATÓRIO** desligar o Debug `DEBUG=0`. e alterar a variavel `SECRET` que deve ser unica para cada ambiente.

Com o serviço desligado execute o comando abaixo para gerar uma SECRET, copie e cole no .env

```bash
docker-compose run backend python -c "import secrets; print(secrets.token_urlsafe())"
```

```bash
docker-compose run backend python manage.py createsuperuser
```

Crie o arquivo de configuração do Ngnix `nginx.conf` baseado no arquivo `nginx_production.conf`

Inicie todos os serviços

```bash
docker-compose up -d
```

Configure uma URL que direcione para a maquina onde está instalado na porta configurada para o Ngnix no docker-compose.

No final deste exemplo a pasta pzserver ficou desta forma:

```bash
-rw-r--r--  docker-compose.yml 
-rw-r--r--  nginx.conf # Arquivo de configuração do Ngnix.
-rw-r--r--  .env # Arquivo com as variaveis de configuração
drwxr-xr-x  archive # Diretório onde ficam os arquivos gerados pela aplicação.
drwx------  pg_data # Diretório onde ficam os arquivos do postgresql em container
drwxr-xr-x  pg_backups # Diretório onde ficam os arquivos do postgresql em container
```

## Update Production Enviroment

Procedimento para atualizar o ambiente de produção ou qualquer outro que utilize imagens builded.

- Editar o arquivo docker-compose.yml e alterar a tag das imagens frontend e backend.
- Editar o arquivo `.env` para adicionar novas variaveis ou altera-las se necessário.
- Executar o pull das novas imagens com o comando `docker-compose pull`.
- Restart dos serviços `docker-compose stop && docker-compose up -d`.
