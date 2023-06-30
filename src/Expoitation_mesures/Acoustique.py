# -*- coding: utf-8 -*-
"""
Created on 26 sept. 2022

@author: martin.schoreisz
module de traitement des donn�es acoustiques stock�es dans la base
"""

import pandas as pd
from Import_stockage_donnees.Params import bdd, startDateMesure, endDateMesure
from Connexions.Connexion_Transfert import ConnexionBdd
from Outils.Outils import checkParamValues

with ConnexionBdd(bdd) as c:
    typeAgregList = pd.read_sql(
        "select code from agreg_bruit.enum_periode_agreg", c.sqlAlchemyConn
    ).code.tolist()


def recupDonneesAcoustiqueSiteInstru(site):
    """
    récupérer les données acoustiques de mesures d'un des 4 sites instrument�.
    in :
        site : integer. Le code correspondant  à  un materiel sur un site. cf table instrumentation_site de la bdd
    """
    with ConnexionBdd(bdd) as c:
        dfDonneesBrutes = pd.read_sql(
            f"SELECT id_site, id, date_heure, leq_a FROM mesures_physiques.niveau_bruit_site WHERE id_site = {site} ORDER BY date_heure",
            c.sqlAlchemyConn,
        )
    return dfDonneesBrutes


def recupDonneesAgregees(site, typeAgreg):
    """
    recuperer des données agregees depuis la bdd
    in :
        site : integer. Le code correspondant à un materiel sur un site. cf table instrumentation_site de la bdd
        typeAgreg : string. parmi typeAgregList
    """
    checkParamValues(typeAgreg, typeAgregList)
    with ConnexionBdd(bdd) as c:
        dfDonneesBrutes = pd.read_sql(
            f"SELECT * FROM agreg_bruit.leq_a WHERE id_instru_site = {site} and periode_agreg = '{typeAgreg}' ORDER BY date_heure",
            c.sqlAlchemyConn,
        )
    return dfDonneesBrutes


def recupFractileAgregees(site, typeAgreg):
    """
    recuperer des données agregees depuis la bdd
    in :
        site : integer. Le code correspondant à un materiel sur un site. cf table instrumentation_site de la bdd
        typeAgreg : string. parmi typeAgregList
    """
    checkParamValues(typeAgreg, typeAgregList)
    with ConnexionBdd(bdd) as c:
        dfDonneesBrutes = pd.read_sql(
            f"SELECT * FROM agreg_bruit.indic_fractile WHERE id_instru_site = {site} and periode_agreg = '{typeAgreg}' ORDER BY date_heure",
            c.sqlAlchemyConn,
        )
    return dfDonneesBrutes


def categorie_jour(date_heure):
    """
    selon une date, savoir si le jour est en jours ouvré, samedi ou dimanche, 6h-18h, 18h-22, 22h-6h
    in :
        date_heure : datetime
    """
    if date_heure.dayofweek in range(0, 5) and 6 < date_heure.hour <= 18:
        return "JO_6h-18h"
    elif date_heure.dayofweek in range(0, 5) and 18 < date_heure.hour <= 22:
        return "JO_18h-22h"
    elif date_heure.dayofweek in range(1, 5) and (
        22 < date_heure.hour or date_heure.hour <= 6
    ):
        return "JO_22h-6h"
    elif date_heure.dayofweek == 5 and date_heure.hour <= 6:
        return "JO_22h-6h"
    elif date_heure.dayofweek == 0 and 22 < date_heure.hour:
        return "JO_22h-6h"
    elif date_heure.dayofweek == 5 and 6 < date_heure.hour <= 18:
        return "samedi_6h-18h"
    elif date_heure.dayofweek == 5 and 18 < date_heure.hour <= 22:
        return "samedi_18h-22h"
    elif (date_heure.dayofweek == 5 and 22 < date_heure.hour) or (
        date_heure.dayofweek == 6 and date_heure.hour <= 6
    ):
        return "samedi_22h-6h"
    elif date_heure.dayofweek == 6 and 6 < date_heure.hour <= 18:
        return "dimanche_6h-18h"
    elif date_heure.dayofweek == 6 and 18 < date_heure.hour <= 22:
        return "dimanche_18h-22h"
    elif (date_heure.dayofweek == 6 and 22 < date_heure.hour) or (
        date_heure.dayofweek == 0 and date_heure.hour <= 6
    ):
        return "dimanche_22h-6h"


def recupHarmonica(site=None, date_deb=None, date_fin=None):
    """
    Récupération de l'indicateur Harmonica depuis la bdd
    in :
        site : None ou int : valur de id_site. cf bdd
        date_deb : None ou str : date de début au format YYYY-MM-DD[ HH:MM:SS]
        date_fin : None ou str : date de fin au format YYYY-MM-DD[ HH:MM:SS]
    """
    with ConnexionBdd(bdd) as c:
        if not site and not date_deb and not date_fin:
            return pd.read_sql(
                f"SELECT * FROM agreg_bruit.harmonica ;", c.sqlAlchemyConn
            )
        elif site and not date_deb and not date_fin:
            return pd.read_sql(
                f"SELECT * FROM agreg_bruit.harmonica WHERE id_site = {site} ;",
                c.sqlAlchemyConn,
            )
        elif not site and date_deb and not date_fin:
            return pd.read_sql(
                f"SELECT * FROM agreg_bruit.harmonica WHERE date_heure >= '{date_deb}' ;",
                c.sqlAlchemyConn,
            )
        elif not site and not date_deb and date_fin:
            return pd.read_sql(
                f"SELECT * FROM agreg_bruit.harmonica WHERE date_heure < '{date_fin}' ;",
                c.sqlAlchemyConn,
            )
        elif site and date_deb and not date_fin:
            return pd.read_sql(
                f"SELECT * FROM agreg_bruit.harmonica WHERE id_site = {site} AND date_heure >= '{date_deb}'; ",
                c.sqlAlchemyConn,
            )
        elif site and not date_deb and date_fin:
            return pd.read_sql(
                f"SELECT * FROM agreg_bruit.harmonica WHERE id_site = {site} AND date_heure < '{date_fin}'; ",
                c.sqlAlchemyConn,
            )
        elif site and date_deb and date_fin:
            return pd.read_sql(
                f"SELECT * FROM agreg_bruit.harmonica WHERE id_site = {site} AND date_heure >= '{date_deb}' AND date_heure < '{date_fin}'; ",
                c.sqlAlchemyConn,
            )
