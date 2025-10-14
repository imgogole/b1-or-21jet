# Seeking head

L'algorithme de la **Tête chercheuse** consiste à accumuler les temps réels des trajets entre chaque station.
En théorie, on tombe sur une valeur proche de la réalité, c'est à dire le temps réel à laquelle le bus va mettre entre Métro Rond Point du Prado et Luminy. Cependant, l'API de la RTM limite la vue des derniers bus traquables à 2. Cela veut dire que traquer un bus devient impossible si le prochain bus à prendre à MRPDP n'est pas au plus l'avant-dernier bus qui arrivera à Luminy.

Par conséquent, nous allons traquer le bus jusqu'à qu'il ne soit plus traquable à une station S_n. A partir de cette station, nous allons regarder les écarts théoriques. Les écarts théoriques seront des moyennes des écarts à tout temps, car on considère que l'heure qu'il est n'influence pas ces valeurs et qu'elles resteront, dans le meilleur des cas, constantes.

## Algorithme

Soit Acc_B1 le temps final que mettra le B1 pour faire le trajet (entre MRPDP et Luminy), de même pour Acc_21Jet.

> Acc_B1 = T_B1_MRPDP + Somme(i=1 à n; c_i)

__Avec :__
- T_B1_MRPDP : le temps à laquelle le prochain bus B1 arrivera à MRPDP
- n : le nombre de stations entre MRPDP et Luminy (excluant MRPDP)
- c_i : l'écart de temps d'un bus entre une station S_i et S_(i-1)

On peut également écrire c_i par :

> c_i = T_B1_S_i - T_B1_S_(i-1)

__Avec :__
- T_B1_S_k : le temps à laquelle le prochain bus B1 arrivera à la station S_k

(Valable de même pour le 21Jet)

En pratique, T_S_k doit être d'abord récupérer en temps réel