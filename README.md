# 🧹 Sr. Ditkovich - El Bot de Neteja del Pis

Aquest és un bot de Telegram passiu-agressiu basat en el mític casero de Spider-Man, el **Sr. Ditkovich**. El seu únic objectiu a la vida és controlar el calendari de neteja del pis i assetjar diàriament a qui no hagi complert amb les seves tasques (Bany, Cuina o Menjador).

> *"Aquest pis és un país lliure, de lloguer barat, però no lliure de porqueria. NETEJA!"*

---

## 📅 Funcionament del Calendari

El bot segueix el calendari oficial de la pissarra del pis per als tres membres: **Xavi, Pau i Mars**.
* **Inici del període:** El bot envia un avís automàtic a les 09:00h indicant quina zona té assignada cada persona (🧻 Bany, 🍳 Cuina, 📺 Menjador).
* **Fi del període:** Si s'ha passat la data límit i algú encara té la seva zona pendent, el bot enviarà un recordatori destructiu cada matí a les 09:00h fins que tothom hagi netejat.

---

## 🛠️ Comandaments Disponibles

Pots interactuar amb el Sr. Ditkovich utilitzant els següents comandaments a Telegram:

* `/start` — Activa el bot al grup del pis i el registra a la base de dades.
* `/estat` — Mostra l'estat actual del període (qui ha netejat i qui té tasques pendents).
* `/fet [Nom]` — Marca la teva zona com a neta. (Exemple: `/fet Xavi`, `/fet Pau` o `/fet Mars`).
* `/afegir_periode [Inici] [Fi] [Bany] [Cuina] [Menjador]` — Afegeix un nou període al calendari directament des de Telegram.
  * *Exemple:* `/afegir_periode 2026-09-15 2026-09-18 Xavi Pau Mars`

---

## 🚀 Requisits i Instal·lació

Si vols executar aquest bot en local, necessites tenir **Python 3.10+** instal·lat i la llibreria de Telegram amb suport per a tasques diàries:

```bash
pip install "python-telegram-bot[job-queue]"
