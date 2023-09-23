# Music Bot Discord

Um Bot para discord que tem a unica função de tocar vídeo/música e/ou alguns tipos de stream. Como: Youtube, SoundCloud, Spotify, Twitch, HTTP Stream...

## Instalação

Clone o projeto

```bash
  git clone https://github.com/GabrielBarros00/Music-Discord-BOT
```

```bash
  cd Music-Discord-BOT
```


Testado no Python 3.11.5 (Recomendado 3.10 ou superior).
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

Realizar o download do Lavalink e a excução antes de executarmos o bot. Testado na versão 3.7.8 do LavaLink.
Link do Github do Lavalink: https://github.com/lavalink-devs/Lavalink/releases

## Corrigindo erro no WaveLink na versão 2.6.4

Dentro da pasta venv, necessário abrirmos o seguinte arquivo: 

No Linux:
```bash
venv/lib/python3.11/site-packages/wavelink/tracks.py
```

No Windows:
```bat
venv\Lib\site-packages\tracks.py
```

Alterar a linha 205 para:
```python
if str(check.host) == 'youtube.com' or str(check.host) == 'www.youtube.com' and check.query.get("list") and not check.query.get("v") or \
```

Alterar a linha 210 para:
```python
elif str(check.host) == 'soundcloud.com' and 'sets' in check.parts and check.query.get("in") == None or str(check.host) == 'www.soundcloud.com' and 'sets' in check.parts and check.query.get("in") == None:
```

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
