import asyncio
import logging
from typing import Dict, List

from fetch.main import main as run_fetcher

user_groups: Dict[str, List[str]] = {
    "Dziennikarze": [
        "hannawawrowska",
        "wozpiotr",
        "KarolinaEKowal1",
        "DSubbotko",
        "piotrbratkowsk1",
        "Walewski_P",
        "marek_kozubal",
        "kowalewski07",
        "JolantaOjczyk",
        "SwiniarskiP",
        "PiotrWolosik",
        "estera_flieger",
        "MrowickiRafal",
        "_ZajacPiotr",
        "WitoldUrbanowic",
        "EwaBugala",
        "woj_raf",
        "piotrdrabik",
        "jzpinski",
        "Olo_Gurgul",
        "PawlowskiJakub",
        "CezOlbrycht",
        "P_Bednarz",
        "Olejarczyk_Onet",
        "gabbsby",
        "BartG_ski",
        "robert_silski",
        "OrchowskiThomas",
        "Karol_Gac",
        "Karol_Gac",
        "Kolodziejski_",
        "gospoprostu",
        "adamskilukasz1",
        "KOsiejuk",
        "KarolKanski",
        "Bart_Wielinski",
        "magda_razem",
        "MForSud",
        "d_kossakowska",
        "zuzanna_dab",
        "mrowka_k",
        "ArturStelmasiak",
        "JoannaRadio",
        "bartoshchyz",
        "GrzeJasinski",
        "WBiedron",
        "pijawor",
        "EwaZajaczkowska",
        "L_Szpyrka",
        "BartoszWojsa",
        "WMarchewczyk",
        "mwpotocki",
        "ARatusznik",
        "JakubNizinski",
        "gazetapl_news",
        "gazeta_wyborcza",
        "GPtygodnik",
        "Dziennik_N",
        "zachodni",
        "DziennikLublin",
        "PR24_pl",
        "TygodnikWPROST",
        "Polityka_pl",
        "24tp_pl",
        "Tygodnik_Sieci",
        "Tysol",
        "TygodnikTVP",
        "RMF24pl",
        "FAKT24PL",
        "DoRzeczy_pl",
        "lis_tomasz",
        "cezarygmyz",
        "lkwarzecha",
        "bweglarczyk",
        "sekielski",
        "r_klonowski",
        "magdalenazbylu1",
        "kamil_zatonski",
        "JacekKarnowski",
        "MR_Minela_20",
    ],
    "Influencerzy": [
        "Palikot_Janusz",
        "BoniekZibi",
        "JaroslawKuzniar",
        "R_A_Ziemkiewicz",
        "pikus_pol",
        "cezarykrysztopa",
        "katarynaaa",
        "Polsport",
        "wtruszczynska",
        "Wonziu",
        "popydo",
        "przemekspider",
        "robsoniqe",
        "paweltkaczyk",
        "ZbigniewHoldys",
        "TheCejrowski",
        "LukaszBok",
        "totylkoteoria",
    ],
    "Inni_Politycy": ["sikorskiradek", "szymon_holownia", "GiertychRoman", "prezydentpl"],
    "KO": [
        "UrszulaAugustyn",
        "piotr_borys",
        "bbudka",
        "ZofiaCzernow",
        "FiliksMagdalena",
        "KonradFrysztak",
        "AGajewska",
        "gajewska_kinga",
        "gapinska_e",
        "c_grabarczyk",
        "JanGrabiec",
        "hennigkloska",
        "JarosMichal",
        "M_K_Blonska",
        "MKierwinski",
        "krawczyk_michal",
        "MarekKrzakala",
        "LasekMaciej",
        "ArturLacki",
        "LoskoMagdalena",
        "A_Marchewka",
        "JagnaMarczulajt",
        "OlekMiszalski",
        "ArkadiuszMyrcha",
        "DorotaNiedziela",
        "SlawomirNitras",
        "pomaska",
        "PawelPoncyljusz",
        "jacek_protas",
        "moanrosa",
        "DariuszRosati",
        "WojciechSaluga",
        "SchetynadlaPO",
        "ikatarasinska",
        "MGolbik",
        "KLubnauer",
    ],
    "Konfederacja": [
        "KonradBerkowicz",
        "krzysztofbosak",
        "GrzegorzBraun_",
        "ArturDziambor",
        "JkmMikke",
        "urbaniak_michal",
    ],
    "Lekarze": [
        "damian_patecki",
        "JaBilinski",
        "bfialek",
        "kosik_md",
        "churreml",
        "DkorycinskaK",
        "calipso_vera",
        "MZ_GOV_PL",
        "NFZ_Centrala",
        "CowZdrowiu",
        "Rzecznik_GUMed",
        "MariaKlosinska",
        "JadwigaSokolow1",
        "KatarzynaPikul1",
        "db_jolanta",
        "PR_OZZL",
    ],
    "Lewica": [
        "KGawkowski",
        "m_gdula",
        "HannaGillPiatek",
        "dgpopiolek",
        "KopiecMaciej",
        "KotulaKat",
        "KretkowskaK",
        "KrutulPawel",
        "AnitaKDZG",
        "MarcinKulasek",
        "KwiatkowskiRob",
        "B_Maciejewska",
        "WandaNowicka",
        "ObazRobert2",
        "pawlowska_pl",
        "ARozenek",
        "MarekRutka",
        "K_Smiszek",
        "wieczorekdarek",
        "mmzawisza",
    ],
    "PIS": [
        "pisorgpl",
        "AMAdamczyk",
        "Andruszkiewicz1",
        "BartosikRyszard",
        "JerzyBielecki2",
        "mblaszczak",
        "BorowiakJoanna",
        "KamilBortniczuk",
        "BorysSzopa",
        "BurzynskaLidia",
        "PCzarnecki83",
        "CzarneckiWIT0LD",
        "CzarnekP",
        "RzecznikPiS",
        "l_dobrzynski",
        "DrabekBB",
        "michaldworczyk",
        "JEmilewicz",
        "PiotrGlinski",
        "MMGosiewska",
        "Jaroslaw_Gowin",
        "GutMostowy",
        "mhorala",
        "PHreniak",
        "FilipKaczynski",
        "piotr_kaleta_",
        "sjkaleta",
        "KrajewskiWies",
        "MartaKubiak8",
        "JacekKurzepa",
        "Anna1Kwiecien",
        "KwitelMarek",
        "JoannaLichocka",
        "lisieckipawel",
        "MarzenaMachalek",
        "BeataPielucha",
        "IwonaMichalek",
        "a_milczanowska",
        "MosinskiJan",
        "arekmularczyk",
        "PiotrMuller",
        "wmurdzek",
        "OzdobaJacek",
        "waldemar_buda",
        "AnnaPaluchSejm",
        "D_Piontkowski",
        "V_Porowska",
        "RauZbigniew",
        "UrszulaRusecka",
        "PiotrSak5",
        "SasinJacek",
        "radekfogiel",
        "AnnaGembicka",
        "m_kaluzny",
        "JKowalski_posel",
        "Macierewicz_A",
        "malecki_m",
    ],
    "PSL_Kukiz": [
        "GrzybAndrzej",
        "DariuszKlimczak",
        "KosiniakKamysz",
        "StefanKrajewski",
        "lubczyk_radek",
        "JanekLopata",
        "UNowogorska",
        "KrzysztofPaszyk",
        "ProtasiewiczJ",
        "SawickiMarek",
        "PZgorzelskiP",
    ]
}


def build_queries(query_phrase: str, users: List[str], lang: str or None = None, max_query_length=500):
    if lang:
        base = f"{query_phrase} lang:{lang}"
    else:
        base = f"{query_phrase}"

    base_length = len(base) + len("()")
    current_length = base_length
    current_users = []

    for user in users:
        user_length = len(user) + len(" OR ")
        if current_length + user_length < max_query_length:
            current_users.append(user)
            current_length += user_length
        else:
            yield f"{base} ({' OR '.join(current_users)})"
            current_users = [user]
            current_length = base_length + user_length

    if len(current_users) > 0:
        yield f"{base} ({' OR '.join(current_users)})"


if __name__ == "__main__":
    phrase = "koronawirus"

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    for group, users in user_groups.items():
        logger.info('Fetching tweets for group: %s having %d users...', group, len(users))
        for query in build_queries(phrase, users, max_query_length=216):
            tweet_count = asyncio.run(run_fetcher(query, twitter_api=True, collection=group,
                                                  product='7day', max_tweets=300_000, lang='pl'))
            logger.info('Fetched %d tweets for group %s...', tweet_count, group)

    logger.info('Fetching tweets without user constraints!!')
    tweet_count = asyncio.run(run_fetcher(phrase, twitter_api=True, collection='wszyscy',
                                          product='7day', max_tweets=300_000, lang='pl'))
    logger.info('Fetched %d tweets without user constraints...', tweet_count)
