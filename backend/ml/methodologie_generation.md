# Méthodologie de génération des profils synthétiques — ORIENT'IA

## 1. Méthode de génération

Génération procédurale (`generate_synthetic_profiles.py`) par tirage aléatoire pondéré :

1. Tirage **uniforme par domaine** (5 domaines), puis tirage uniforme du parcours
   à l'intérieur du domaine. Ce choix — domaine d'abord — évite de sur-représenter
   l'informatique (4 parcours) par rapport à un domaine à parcours unique (TEH).
2. Pour chaque domaine, un dictionnaire d'« affinité » fixe la probabilité qu'un
   candidat typique de ce domaine coche chaque item (matière, compétence, centre
   d'intérêt, environnement souhaité). Chaque feature est tirée indépendamment
   selon cette probabilité (tirage de Bernoulli).
3. La moyenne scolaire est tirée dans une plage plausible par domaine, bruitée
   par un terme gaussien (σ = 1.2).
4. 15 % des profils sont des **profils frontière** : leurs probabilités
   d'affinité sont un mélange à 60/40 entre le domaine visé et un domaine
   proche (ex. informatique / gestion-finance), pour éviter des profils trop
   caricaturaux.
5. 10 % des profils simulent un **« mauvais choix »** : le parcours finalement
   retenu est tiré dans un domaine différent du domaine d'affinité du profil.
   Cela imite le fait, souligné dans le sujet, qu'un choix réel de parcours
   n'est pas toujours celui qui correspond le mieux au profil.
6. 8 % de valeurs manquantes sont injectées, champ par champ, sur les
   features optionnelles (matières, compétences, intérêts), pour refléter un
   profil collecté progressivement et potentiellement incomplet.

## 2. Hypothèses assumées

- Les probabilités d'affinité par domaine sont **fixées à dire d'expert**
  (lecture du référentiel des matières ISPM), pas mesurées sur données
  réelles. C'est l'hypothèse la plus forte du jeu de données.
- Indépendance approximative entre features au sein d'un domaine (pas de
  corrélations fines modélisées entre, par ex., "aime les maths" et "aime la
  physique").
- La moyenne scolaire est traitée comme faiblement informative et bruitée
  volontairement — un signal réel serait probablement plus subtil.

## 3. Biais potentiellement introduits

- **Biais de construction du vocabulaire** : le vocabulaire "profil candidat"
  (11 matières, 6 compétences, 6 intérêts) est une simplification du
  référentiel réel ; des nuances peuvent être perdues.
- **Déséquilibre structurel domaine/parcours** : TEH capte à lui seul tout le
  volume du domaine tourisme, alors que l'informatique répartit son volume
  sur 4 parcours → déséquilibre de classes à traiter explicitement en
  évaluation (F1 macro, pas seulement accuracy).
- **Absence de biais démographiques** : volontairement, aucune variable de
  genre, âge ou origine n'a été introduite dans la génération, conformément
  à l'interdiction du sujet d'utiliser des caractéristiques personnelles
  sensibles comme critère.
- **Risque de "jeu trop propre"** : malgré le bruit injecté, ce jeu reste
  généré par des règles connues. C'est précisément pour cela que le sujet
  impose une **validation/test sur les réponses d'enquête réelles** — seule
  mesure valable de la capacité de généralisation du modèle.

## 4. Contrôles de cohérence appliqués

Fonction `sanity_checks()` exécutée avant toute livraison :
- chaque `parcours` généré existe dans le référentiel ;
- `domaine` et `parcours` restent cohérents entre eux ;
- `moyenne_generale` reste dans les bornes plausibles (6–18) ;
- distribution finale par parcours inspectée manuellement (voir sortie du
  script) pour repérer tout déséquilibre anormal avant l'entraînement.

## 5. Utilisation prévue

Ce jeu sert **exclusivement à l'entraînement**. Le protocole complet est :

| Sous-ensemble | Origine |
|---|---|
| Entraînement | `synthetic_profiles.csv` (ce jeu) |
| Validation / Test | Réponses de l'enquête réelle (étudiants + professionnels) |

L'écart de performance entre validation croisée sur le synthétique et
performance sur l'enquête réelle est la mesure clé de généralisation à
rapporter (section 14 du sujet).
