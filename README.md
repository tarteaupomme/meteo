# meteo
Station meteo basée sur un bmp180 avec interface web prevue pour un raspberry pi 3.

## releve.py
Effectue les relevés de température et pression atmosphérique.

## main.py
Serveur web qui utilise Flask.
URLs:
- / accueil, graphique des dernières 48h
- /stats statistique (record, statistiques mensuels ...)
- /archives/année/moi/jour/heure/?freq=(1/frequence des mesures seront affichées) archives, possibilité de mettre un * ou une plage (ex: 5-12), freq permet de limiter le trop grand nombre de donées
- /about nombre de mesures effectuées et date de la premiere...

## info.py
Permet de recuperer quelques information basiques sans utiliser l'interface web.
