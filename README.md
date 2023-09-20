# Music Bot Discords

Um Bot para discord que tem a unica função de tocar vídeo/música e/ou alguns tipos de stream. Como: Youtube, SoundCloud, Spotify, Twitch, HTTP Stream...

## Instalação

Clone o projeto

```bash
  git clone https://github.com/GabrielBarros00/Music-Discord-BOT
```

```bash
  cd Music-Discord-BOT
```


Recomendado Python 3.10 ou mais recente.
```bash
python -m venv venv
```

E acessar a venv para a instalação das bibliotecas necessárias para execução.

Linux:
```bash
source venv/bin/activate
```

Windows:
```bat
.\venv\Scripts\activate
```
Na sequencia instalar as libs:

```bash
pip install -r requirements.txt
```

Realizar o download do Lavalink e a excução antes de executarmos o bot.
Link do Github do Lavalink: https://github.com/lavalink-devs/Lavalink/releases
## Variáveis de Ambiente

Para rodar esse projeto, você vai precisar adicionar as seguintes variáveis de ambiente no seu .env

`SPOTIFY_CLIENT_ID`

`SPOTIFY_CLIENT_SECRET`

`BOT_TOKEN`

`LAVALINK_URL`

`LAVALINK_PASSWORD`


## Rodando localmente

Com a **venv** ativada, agora podemos iniciar o bot utilizando o seguinte comando na pasta raiz do projeto:

```bash
python __main__.py
```
