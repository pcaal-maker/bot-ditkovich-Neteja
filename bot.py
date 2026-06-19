import logging
import json
import os
import random
from datetime import datetime, time
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Configurar registres per veure errors si de cas
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

DATA_FILE = "ditkovich_neteja.json"

# Calendari inicial per defecte (si no existeix l'arxiu JSON)
CALENDARI_DEFECTE = [
    {"inici": "2026-05-29", "fi": "2026-06-11", "responsables": ["Xavi", "Pau", "Mars"]},
    {"inici": "2026-06-25", "fi": "2026-06-28", "responsables": ["Mars", "Xavi", "Pau"]},
    {"inici": "2026-07-09", "fi": "2026-07-12", "responsables": ["Pau", "Mars", "Xavi"]},
    {"inici": "2026-07-23", "fi": "2026-07-26", "responsables": ["Xavi", "Pau", "Mars"]},
    {"inici": "2026-08-06", "fi": "2026-08-09", "responsables": ["Mars", "Xavi", "Pau"]},
    {"inici": "2026-08-20", "fi": "2026-08-23", "responsables": ["Pau", "Mars", "Xavi"]},
    {"inici": "2026-09-03", "fi": "2026-09-06", "responsables": ["Xavi", "Pau", "Mars"]}
]

FRASES_INICI = [
    "He sentit que comença el període de neteja. Netegeu! Aquest pis és un país lliure, de lloguer barat, però no lliure de porqueria.",
    "Comença el torn! Si voleu que arregli el calentador de l'aigua, primer vull veure tot el pis brillant!",
    "No em vinguis amb excuses de que ets 'bona gent'. Si el període comença avui, vull veure el terra net ARA.",
    "El calendari del passadís diu que toca netejar. On són els meus voluntaris?",
    "Nou període de neteja actiu. Menys mirar el mòbil i més agafar l'escombra. El sabó no es gasta sol!",
    "Ah, el dia de la neteja... El meu dia preferit. A veure si aquest cop ho feu millor que l'altra setmana, que feia pena.",
    "He obert el calendari i us toca pencar. Si jo hagués de netejar el replà amb les vostres ganes, viuríem en un abocador.",
    "Vull veure reflectit el meu rostre al terra de la cuina abans que acabi el termini. Comenceu ja!",
    "Rellotge en marxa! No vull veure ni una taca ni un cabell al bany. Ràpid, ràpid!",
    "La meva filla diu que ja és l'hora. Jo no vull problemes, només vull que compliu amb el calendari de la pissarra."
]

FRASES_COSSETJAMENT = [
    "⚠️ El termini HA ACABAT i encara veig merda! NETEJA! HAURÉ DE LLOGAR-LI EL PIS A UNS EFICIENTS EXPATS ALEMANYS?!",
    "Estàs lliure d'obligacions? No ho crec. Neteja! Tens problemes amb la higiene, exactament igual que el Peter Parker amb el lloguer.",
    "Neteja! No em diguis que ho faràs demà. Si les ganes de netejar fossin promeses, la meva dona no m'hagués deixat.",
    "Hi ha gent que s'espera que jo agafi el motxo. NETEJA! Dona'm el pis net!",
    "El GREIX de la cuina s'està acumulant... NETEJA! Primer neteges, i després parlem del mercat immobiliari i altres merdes woke!",
    "NETEJA! Si no veig el menjador net en 24 hores, apujo el lloguer un 50% per danys morals!",
    "Escolta'm bé: el termini ha vençut. No vull històries, no vull poemes, vull veure el bany polit. NETEJA!",
    "He passat pel passadís i gairebé em desmaio de la pudor. NETEJA! On són els meus herois del clor?!",
    "Esteu vius o se us han menjat els CUCS? El termini ha acabat! NETEJA! No em facis pujar amb la llibreta de desnonaments.",
    "NETEJA! De què us serveix tenir un pis si el teniu com una quadra de cavalls? Més fregar i menys rondinar!"
]

FRASES_TOT_NET = [
    "Heu marcat les tres zones com a fetes. Sincerament, no em crec que hàgiu passat el motxo, però administrativament esteu lliures per avui.",
    "La pissarra diu que heu complert amb el període actual. Això no és cap miracle, és la vostra pasterada d'obligació. Verificaré el greix de la cuina més tard.",
    "Tots tres heu enviat el comandament... Molt bonic sobre el paper. Una altra cosa és la colònia de fongs que teniu muntada darrere del vàter.",
    "D'acord, el sistema diu que el període està tancat i net. No us flipeu ni us pengeu medalles, que demà ja tornareu a tenir el pis com una quadra.",
    "He vist els tres xecs verds. Per avui heu salvat el coll, però no em caieu bé igualment. A veure quant dura aquesta falsa sensació d'higiene.",
    "Avui no us puc renyar perquè la llista està completada. Disfruteu de la treva, que la pròxima setmana us vull veure suar clor de veritat.",
    "Heu complert amb el tràmit d'aquests dies. Felicitats, actueu com a persones civilitzades per un cop a la vida. No us acostumeu al civisme."
]

FRASES_TREVA = [
    "Ara mateix estic tranquil. El pròxim calvari comença el {data}. Aprofiteu per acumular brossa i viure en la immundícia.",
    "No teniu deures oficials fins al {data}. Podeu deixar que els bacteris formin una nova civilització a la pica de la cuina.",
    "Treva oficial a la llibreta. El pròxim període comença el {data}. Teniu permís per ser unes rates fins llavors.",
    "Segons la pissarra esteu lliures fins al {data}. No us flipeu, que sé que esteu utilitzant caixes de pizza buides com a tauletes de nit.",
    "Fins al {data} no penso pujar a inspeccionar. Aprofiteu per acumular brossa com autèntics mapatxes brossaires.",
    "Silenci administratiu fins al {data}. Teniu uns dies de marge per deixar el pis com una quadra abans que torni la llei del clor.",
    "Ara mateix no us puc desnonar per porqueria, el pròxim assalt és el {data}. Aneu criant cucs tranquil·lament."
]

def carregar_estat():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            estat = json.load(f)
            if "calendari" not in estat:
                estat["calendari"] = CALENDARI_DEFECTE
            return estat
    return {"fet": [], "periode_actual_inici": "", "chat_id": None, "calendari": CALENDARI_DEFECTE}

def guardar_estat(estat):
    with open(DATA_FILE, "w") as f:
        json.dump(estat, f)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    estat = carregar_estat()
    estat["chat_id"] = update.effective_chat.id
    guardar_estat(estat)
    await update.message.reply_text(
        "Hi ha algú en aquest cau de porcs? Sóc el Sr. Ditkovich. Vigilaré aquest grup cada dia per veure si netegeu.\n\n"
        "Feu servir `/fet Mars`, `/fet Xavi` o `/fet Pau` quan hàgiu acabat la vostra zona assignada. O si no... NETEJA!",
        parse_mode="Markdown"
    )

async def estat_manual(update: Update, context: ContextTypes.DEFAULT_TYPE):
    avui_str = datetime.now().strftime("%Y-%m-%d")
    estat = carregar_estat()
    calendari = estat["calendari"]
    
    periode = None
    for p in calendari:
        if p["inici"] <= avui_str <= p["fi"] or (avui_str > p["fi"] and p["inici"] == estat.get("periode_actual_inici")):
            periode = p
            break
            
    if not periode:
        següents = [p for p in calendari if p["inici"] > avui_str]
        if següents:
            frase_escollida = random.choice(FRASES_TREVA).format(data=següents[0]['inici'])
            await update.message.reply_text(frase_escollida)
        else:
            await update.message.reply_text("S'ha acabat el calendari de la pissarra. Aneu a pintar-ne una altra demanant-li diners al Parker.")
        return

    pendents = [r for r in periode["responsables"] if r not in estat["fet"]]
    
    if not pendents:
        await update.message.reply_text(random.choice(FRASES_TOT_NET))
    else:
        bany_resp = periode["responsables"][0]
        cuina_resp = periode["responsables"][1]
        menjador_resp = periode["responsables"][2]
        
        txt = f"📋 **Estat del període ({periode['inici']} al {periode['fi']}):**\n"
        txt += f"🧻 **Bany:** {bany_resp} {'✅' if bany_resp in estat['fet'] else '❌ PENDENT'}\n"
        txt += f"🍳 **Cuina:** {cuina_resp} {'✅' if cuina_resp in estat['fet'] else '❌ PENDENT'}\n"
        txt += f"📺 **Menjador:** {menjador_resp} {'✅' if menjador_resp in estat['fet'] else '❌ PENDENT'}\n"
        await update.message.reply_text(txt, parse_mode="Markdown")

async def fet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Qui ets? Digues `/fet Mars`, `/fet Xavi` o `/fet Pau`. No em facis perdre el temps.", parse_mode="Markdown")
        return
    
    qui = context.args[0].strip().capitalize()
    
    if qui not in ["Mars", "Xavi", "Pau"]:
        await update.message.reply_text("Ets un impostor? Aquest nom no està autoritzat al pis! Tria entre Mars, Xavi o Pau.")
        return

    estat = carregar_estat()
    if qui in estat["fet"]:
        await update.message.reply_text(f"Ja em vas dir que ho havies fet, {qui}. No em intentis estafar, jo vigilo els passadissos.")
        return

    estat["fet"].append(qui)
    guardar_estat(estat)
    
    frases_gracies = [
        f"Molt bé {qui}... ets bona gent. Però encara em deus la neteja del mes passat.",
        f"D'acord, {qui} s'ha salvat per avui. Ja pots tornar a tancar-te a la teva habitació a escoltar ''música''.",
        f"{qui} ha complert. Apuntat queda. La meva filla ja pot esborrar el teu nom de la llista de desnonaments."
    ]
    await update.message.reply_text(random.choice(frases_gracies))

async def afegir_periode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 5:
        await update.message.reply_text(
            "Falten dades, tros de quòniam! L'estructura correcta és:\n"
            "`/afegir_periode AAAA-MM-DD AAAA-MM-DD NomBany NomCuina NomMenjador`", 
            parse_mode="Markdown"
        )
        return

    inici_rebut = context.args[0]
    fi_rebut = context.args[1]
    resp_bany = context.args[2].capitalize()
    resp_cuina = context.args[3].capitalize()
    resp_menjador = context.args[4].capitalize()

    try:
        datetime.strptime(inici_rebut, "%Y-%m-%d")
        datetime.strptime(fi_rebut, "%Y-%m-%d")
    except ValueError:
        await update.message.reply_text("El format de data és incorrecte! Revisa que sigui `AAAA-MM-DD` (Ex: 2026-09-15).")
        return

    noms_valids = ["Mars", "Xavi", "Pau"]
    if resp_bany not in noms_valids or resp_cuina not in noms_valids or resp_menjador not in noms_valids:
        await update.message.reply_text("Els responsables han de ser Mars, Xavi o Pau. No em portis desconeguts al pis.")
        return

    estat = carregar_estat()
    nou_bloc = {
        "inici": inici_rebut,
        "fi": fi_rebut,
        "responsables": [resp_bany, resp_cuina, resp_menjador]
    }
    
    estat["calendari"].append(nou_bloc)
    estat["calendari"].sort(key=lambda x: x["inici"])
    guardar_estat(estat)

    await update.message.reply_text(
        f"Nou període registrat del {inici_rebut} al {fi_rebut}.\n"
        f"🧻 Bany: {resp_bany} | 🍳 Cuina: {resp_cuina} | 📺 Menjador: {resp_menjador}.\n"
        "Ja ho tinc guardat a la meva llibreta."
    )

async def revisio_diaria(context: ContextTypes.DEFAULT_TYPE):
    estat = carregar_estat()
    chat_id = estat.get("chat_id")
    if not chat_id:
        return

    avui = datetime.now()
    avui_str = avui.strftime("%Y-%m-%d")
    calendari = estat["calendari"]

    for periode in calendari:
        if avui_str == periode["inici"]:
            estat["fet"] = []
            estat["periode_actual_inici"] = periode["inici"]
            guardar_estat(estat)
            
            bany = periode["responsables"][0]
            cuina = periode["responsables"][1]
            menjador = periode["responsables"][2]
            
            responsables_text = f"🚨 **NOU PERÍODE DE NETEJA ({periode['inici']} al {periode['fi']})** 🚨\n\n" \
                                f"🧻 **Bany:** Toca a *{bany}*\n" \
                                f"🍳 **Cuina:** Toca a *{cuina}*\n" \
                                f"📺 **Menjador:** Toca a *{menjador}*\n\n" \
                                f"_{random.choice(FRASES_INICI)}_"
            await context.bot.send_message(chat_id=chat_id, text=responsables_text, parse_mode="Markdown")
            return

        data_fi = datetime.strptime(periode["fi"], "%Y-%m-%d")
        if avui > data_fi and estat.get("periode_actual_inici") == periode["inici"]:
            pendents = [r for r in periode["responsables"] if r not in estat["fet"]]
            
            if pendents:
                porcs_mencions = ", ".join([f"*{p}*" for p in pendents])
                txt = f"🚨 **AVÍS DIARI DEL SR. DITKOVICH** 🚨\n\n" \
                      f"El termini va acabar el {periode['fi']}. Escolta'm bé, {porcs_mencions}: NO HEU NETEJAT!\n\n" \
                      f"_{random.choice(FRASES_COSSETJAMENT)}_"
                await context.bot.send_message(chat_id=chat_id, text=txt, parse_mode="Markdown")
                return
            else:
                # CORREGIT: Marquem que el període ha finalitzat correctament i continuem mirant el calendari
                estat["periode_actual_inici"] = ""
                guardar_estat(estat)
                continue

def main():
    TOKEN = "7784916847:AAFGT_AlxA6fASNbY58wkKIIEbMJgCv3Xp4"
    
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("estat", estat_manual))
    application.add_handler(CommandHandler("fet", fet))
    application.add_handler(CommandHandler("afegir_periode", afegir_periode))

    job_queue = application.job_queue
    job_queue.run_daily(revisio_diaria, time=time(9, 0, 0))

    print("El Sr. Ditkovich està amagat al replà de l'escala esperant la porqueria...")
    application.run_polling()

if __name__ == '__main__':
    main()
