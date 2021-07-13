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
