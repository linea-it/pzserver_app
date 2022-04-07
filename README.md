

### 

### Setup Database

Inicie o serviço do banco de dados e espere a mensagem `database system is ready to accept connections` para só depois iniciar o backend.

```bash
docker-compose up database
```



# Mudanças 

- Movi o frontend pz-server -> frontend
- Movi o backend pz-server-api -> backend
- Criei um arquivo env_template com as variaveis de ambiente (facilita o deploy pq o nome do arquivo será sempre o mesmo).
- Fixei a versão do postgres para 13.6 similar a nossa versão de produção que é 13.4.
- Fixei a versão da imagem python do backend para python 3.10 a mesma que estava sendo utiliza antes.
- Alterei a criação da imagem do backend para utilizar a versão slim.
- A imagem do backend está usando um venv para as dependencias, isso resolve o warning do pip sobre o uso do root. a vantagem é que a imagem é mais segura já que não é mais possivel adicionar libs depois do build. a desvantagem é que qualquer nova dependencia deve ser adicionada ao requirements.txt e depois feito um build.
- Mudei o diretório static do django para archive/django_static dessa a mudança do nome é por que o react usa um diretório static também e isso causa conflitos.
- Mudei as urls do django rest, todas agora tem o prefixo api/. essa mudança é pq o frontend assume a url raiz /.
- Adicionei um ngnix ao docker-compose, deve ser ligado sempre. ( deixei o pzserver em http://localhost) a porta 80 pode ser mudada no docker-compose caso já esteja em uso. internamente o ngnix está rodando na 8080.


