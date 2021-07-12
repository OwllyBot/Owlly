# OWLLY : The special french bot 

[Invitation](https://discord.com/api/oauth2/authorize?client_id=803714709059928064&permissions=8&scope=bot)

Owlly est un bot qui permet de créer des pièces... Mais pas que !

Initialement pensée pour uniquement créer des channels à partir d'une réaction, mais il s'est étoffé au fur et à mesure des besoins que j'avais pour la gestion administrative de mes RP.

Du coup, voici un petit sommaire des fonctions disponibles ! 

Note : Le préfix par défaut est `?` mais vous pouvez l'éditer à loisir. 

## PIÈCE & CHANNEL 

Il y a deux fonctions : les billets, et les tickets.

### Billets

Les billets permettent de créer un créateur de channels à partir de plusieurs catégories. Pour lancer l'édition, ou la création, il suffit de faire `?billet` pour afficher le menu. La création est très guidée et la recherche des catégories peut se faire via leur nom (même incomplet) ou leur identifiant ! 

La configuration offre une option pour autoriser ou nom le nommage automatique des channels.

### Tickets

A l'instar des billets, ils permettent la création facile des canaux par vos joueurs. Par contre, vous ne pouvez configurer qu'une seule catégorie et il y a plus d'options que pour les billets.

Les options sont donc :
- Nom automatique, ou non, mais aussi une "template" particulière.
- La numérotation automatique, qui peut commencer à un nombre particulier, et se reset à un certain numéro. En outre, une option permet de faire une augmentation spécifique. Ainsi il est possible de créer, par exemple, 10 channels numéroté de 1 à 10, puis augmenter de 100, pour faire 100, 101.... 
- Vous pouvez choisir l'émoji de création, aussi. 

Notons que contrairement aux milliards de bots à tickets, vous ne pouvez pas supprimer un channel en dehors de l'option offerte par les paramètres discords habituels. C'est NORMAL : Les channels sont destinés à être permanents.

## Modification : Les auteurs

Le problème, à la base était : comment un auteur de channel peut modifier son propre channels sans avoir des droits de modération ? Et la réponse est toute simple : en passant par le bot.

L'auteur d'un channel peut donc :
- Mettre un message en pins
- Retirer un pin ! 
- Rajouter une description et la retirer
- Renommer son channel.

## Recherche de mot, dans un channel

Pour les jeux de rôle dont la recherche discord n'est pas très pratique, j'ai créée la fonction "lexique" (ou search) qui permet de chercher des messages avec une template spécifique dans un channel fixé.
Ainsi, si vous avez une liste de mot sous la forme `mot:`, le bot va chercher et ressortir les mots correspondantss.  Pratique, si vous avez un petit lexique ! 

Les autres fonctions sont :
- La suppression automatique des messages de discord sur les pins (je déteste ça)
- Une fonction pour mettre des joueurs en fiche validée, avec une configuration des rôles toujours mis. La fonction permet de créer des rôles à la volée et de les ajouter directement. 


---

En cas de problème, merci de faire un signalement dans l'onglet **Issue** et de ne PAS me MP sur discord. Je ne risque pas de le voir ! 
