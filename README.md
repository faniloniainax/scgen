# SCGen
SCGen (court pour Student Card Generator) est un ensemble de script pythons qui permettent de générer des images recto-verso de cartes d'étudiants pour l'Ecole Nationale d'Informatique.

## Installation
Le script requière une version de Python compatible avec les Type Hints, de préférence `>= 3.7`. Par ailleurs, certains modules externes sont aussi utilisés pour les différentes opérations. Pour installer ces modules, il est nécessaire d'avoir au préalable une installation de `pip`, vérifiable avec la commande:

```shell
$ pip --version
```

Ce qui devrait afficher la version installée de `pip`. Ensuite, il est conseillé (mais pas nécessaire) de créer un environnement virtuel avec `venv`:

```shell
$ python -m venv venv
```

Et d'activer cet environnement virtuel avec la commande appropriée, dans le cas général, sous Windows:

```shell
$ venv/Scripts/activate
```

Ensuite, pour procéder à l'installation des modules, il suffit de lancer la commande:

```shell
$ pip install -r requirements.txt
```

## Utilisation
### Fichier Excel
Pour utiliser le script, il faut s'assurer d'avoir au préalable un fichier `input.xlsx` dans le répertoire courant. Ce fichier sera la source de toutes les données qui seront "collées" sur la carte d'étudiant. 

### Configuration
Par ailleurs, il est aussi nécessaire de modifier la variable `SHEETS_MAP` dans le fichier `scgen_xlconfig.py`, pour spécifier les différentes feuilles du classeur que le script devra lire. A droite, il faut spécifier le nom de la feuille, et à gauche le constructeur de la classe `Class`, qui permettra de référencer certaines informations. Le constructeur prendra en argument le niveau et le parcours.
E.g.: pour ajouter la classe `L3 XD`, dont les données appartiennent à la feuille `L3XD1`, il suffit d'ajouter l'entrée au dictionnaire:
```diff
SHEETS_MAP = {
    "L1PRO": Class("L1", "PRO"),
    # etc...
+   "L3XD1": Class("L3", "XD"),
}

```

### Lancement
Pour éxécuter le script, lancez-le avec la commande:

```shell
$ python scgen_single.py
```

Un log "compréhensif" du statut de la création de chaque carte sera affiché dans la console. Additionnellement, si des erreurs (des exceptions) sont rencontrées durant la lecture d'un étudiant, le message sera envoyé vers la sortie standard des erreurs (`stderr`).

## Notes
Le script possède quelques inconvenients, qui idéalement devraient être réglés dans le futur:
* Les erreurs contiennent juste le message de l'exception. Dans la plupart des cas, ce sera un `string index out of range`, pour les étudiants n'ayant pas un numéro CIN complet.
* L'existence d'une feuille n'est pas vérifiée.
* Les images sont rognées de façon arbitraire. Il n'existe aucun moyen de savoir que le visage d'un individu est bien présent dans l'image finale. Pour éviter les rognages, il faut commenter la [ligne correspondante](scgen_single.py#L196).