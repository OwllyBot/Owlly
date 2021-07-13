Ce dossier sert à avoir une version vidée de la base de données afin de permettre aux personnes extérieur aux bots de faire leur propres test en local. 
En aucun cas cette base de données doit être modifiée ou upload sur le repo : elle ne doit servir QUE d'exemple. 

Pour lancer la création, dans un terminal :
`python3 create_files`

Vous pouvez afficher l'aide avec : 
`python3 create_files help`

Le script va : 
- Créer une base de données nommée Owlly dans `src` (qui sera vide, puisque privé)
- Créer un dossier `fiches` dans `src`
- Ajouter la base de donnée et le dossier à la fin du `.gitignore`

Il est nécessaire que vous ayez votre propre token de bot afin de tester. [Ce tutoriel vous permettra de savoir comment faire](https://www.docstring.fr/blog/creer-un-bot-discord-avec-python/).

Le token peut être simplement mis dans vos variable d'environnement sous le nom de `DISCORD_BOT_TOKEN_TESTING` et `DISCORD_BOT_TOKEN`.
![](https://www.malekal.com/wp-content/uploads/variables-environnement-Windows-4.jpg).
⚠️ Si les variables sont mises en clairs dans votre repo, discord les détectera et les désactivera automatiquement, vous devez donc obligatoirement les mettre dans vos variables d'environnement.

> `DISCORD_BOT_TOKEN` s'utilise uniquement sur la main branch, lorsque testing s'utilise uniquement sur la dev branch.

**Note à propos de [Pyimgur](https://github.com/Damgaard/PyImgur)** :
Afin de ne pas perdre les images des utilisateurs, toutes les images sont transmises anonymement sur Imgur. De fait, vous avez besoin d'un TOKEN d'API.
Pour cela, il suffit d'ajouter votre application et de choisir `Anonymous Usage`. Vous obtiendrez un `client_id` qui devra être enregistré dans vos variables d'environnement sous le nom de `CLIENT_ID`.

⚠️ N'oubliez pas d'installer les modules avec `pip install -r requirements.txt` et/ou de mettre à jour les divers modules utilisés par le bot.