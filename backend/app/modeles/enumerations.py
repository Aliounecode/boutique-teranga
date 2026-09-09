import enum


class StatutProduit(str, enum.Enum):
    DISPONIBLE = "disponible"
    BIENTOT_DISPONIBLE = "bientot_disponible"
    # La rupture n'est PAS ici : elle est calculee depuis le stock des variantes.


class TypeMouvementStock(str, enum.Enum):
    VENTE = "vente"
    REAPPROVISIONNEMENT = "reapprovisionnement"
    RETOUR = "retour"
    CORRECTION = "correction"
    PERTE = "perte"


class StatutVente(str, enum.Enum):
    VALIDEE = "validee"
    ANNULEE = "annulee"


class MoyenPaiement(str, enum.Enum):
    ESPECES = "especes"
    WAVE = "wave"
    ORANGE_MONEY = "orange_money"
    FREE_MONEY = "free_money"
    CARTE = "carte"
    AUTRE = "autre"


class StatutCommande(str, enum.Enum):
    NOUVELLE = "nouvelle"
    VALIDEE = "validee"
    REFUSEE = "refusee"
    ANNULEE = "annulee"