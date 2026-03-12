# Le jeu

## Les commandes

Vous pouvez vous déplacer dans le jeu à l'aide des touches directionelles ou utiliser zqsd

Pour intéragir avec les éléments comme ouvrir les coffres ou intéragir avec les portes

Quand vous possédez plusieurs objets vous pouvez changer l'objet séléctionné avec les touches f et r.

Vous pouvez également lancer l'objet séléctionné avec la touche a.

Sur une échelle vous pouvez descendre ou monter avec les touches directionelles et z et s .

Si vous sautez dans une boite à pièces vous la mettez sur votre tête et la gardez jusqu'à ce que toutes les pièces de celle-ci soit récupérées.

/!\ n'appuyez pas sur echap : vous allez fermer le jeu en mode forcé.

## Les fonctionalitées

### dans le menu de jeu

Vous pouvez changer la langue du jeu et les paramètres graphiques a partir du menu "!" en haut a droite de l'ecran de demarrage.

Dans le menu jouer vous avez également le choix de créer un monde a l'aide de l'éditeur (détaillé dans la partie éditeur), modifier un monde a l'aide de l'éditeur ou de jouer sur une carte personalisés.

### dans le jeu

Vous pouvez ouvrir des coffres, avoir des boîtes a pièces ou ouvrir des portes.

Vous glissez sur la glace et les objets également.
Les monstres quand a eux ne glissent pas grace a leur viscosité.

Vous pouvez également utiliser les cheats

touche t puis entrez la commande

les commandes:
- gamerule fullscreen => plein écran
- give (key ou coins) nombre => donne un nombre de clef ou de pièces au joueur
- player life x => défini a x la vie du joueur
- tp x y => téléporte la position du joueur en x y



# Le code

## Les classes

Le code est divisé en plusieures classes qui ont chaqunes leurs description sur leur fonctionnement.


### La classe App

La classe App est la classe principale du jeu.
Elle sert a lancer le jeu. Initialiser les paramètres et elle permet également de lancer les différentes classe en fonction de la ou l'utilisateur se trouve.


### La classe physic

La classe physic est la classe qui possèdes différentes positions des monstres et permet aussi de récupérer le type des tiles.

### La classe Player

La classe Player est la classe qui gère le joueur et toutes ses intéractions comme la gravité ou le ramassage des objets

### La classe UI

La classe UI est la classe qui permet d'afficher l'interface avec l'inventaire du joueur, sa vie.




## Les fonctions

Il y a deux fonctions qui permettent l'une de récupérer la touche qui a été appuyée.
Elle s'apelle key.
L'autre fonction permet de trouver le texte ascocié a une langue.
Elle s'apelle lang et elle prend en parametre l'identifiant du texte et la langue un str des deux premières lettres de la langue.



# L'éditeur

L'éditeur permet à l'utilisateur de créer ou modifier une carte.

On peut séléctionner une tuile et la placer dans le monde

Si on choisi une tuile de joueur on défini la position du joueur dans le monde
Si on place une tuile de monstre on place un monstre dans le monde

Si on place un coffre ou une boite. L'éditeur va nous demander le nombre de pièces a mettre dedans

Si on place une porte qu'elle soit ouverte ou fermée.
L'éditeur va nous demander le monde de destination et la position de destination.