export const formations = [
  {
    name: "INFORMATIQUE",
    title: "Informatiques et Télécommunications",
    tag: "Numérique · IA · Réseaux",
    score: 92,
    color: "blue",
    paths: 4,
    parcours: ["IGGLIA", "IMTICIA", "ISAIA", "ESIIAG"],
    parcoursDetails: {
      IGGLIA: {
        description:
          "Conception de logiciels, applications et solutions numériques.",
        matieres: "Algorithmique, programmation, bases de données",
        specificites: "Projets pratiques et développement web/mobile",
      },
      IMTICIA: {
        description:
          "Gestion des technologies de l'information et des systèmes connectés.",
        matieres: "Réseaux, systèmes, bases de données",
        specificites:
          "Administration des infrastructures et transformation digitale",
      },
      ISAIA: {
        description:
          "Analyse des données et création de solutions fondées sur l'intelligence artificielle.",
        matieres: "Mathématiques, statistiques, machine learning",
        specificites: "Data, IA appliquée et modèles prédictifs",
      },
      ESIIAG: {
        description:
          "Sécurité, réseaux et gouvernance des systèmes informatiques.",
        matieres: "Réseaux, cybersécurité, systèmes d'exploitation",
        specificites: "Protection des données et audit des systèmes",
      },
    },
    visual: "Code, réseaux et intelligence artificielle",
    desc: "Code, données, systèmes et intelligence artificielle pour les métiers du numérique.",
  },
  {
    name: "GÉNIE",
    title: "Génie Industriel et Civil",
    tag: "Industrie · Construction",
    score: 85,
    color: "orange",
    paths: 3,
    parcours: ["EMII", "GCA", "ICMP"],
    parcoursDetails: {
      EMII: {
        description: "Organisation et maintenance des équipements industriels.",
        matieres: "Mécanique, électrotechnique, automatisme",
        specificites: "Maintenance, production et performance industrielle",
      },
      GCA: {
        description:
          "Conception et réalisation de bâtiments et d'infrastructures.",
        matieres: "Résistance des matériaux, topographie, construction",
        specificites: "Chantiers, plans techniques et gestion des travaux",
      },
      ICMP: {
        description:
          "Pilotage des procédés industriels et des projets techniques.",
        matieres: "Génie des procédés, qualité, gestion de projet",
        specificites: "Optimisation des flux et contrôle de production",
      },
    },
    visual: "Plans, chantier et infrastructures",
    desc: "Énergie, matériaux, maintenance et infrastructures durables pour bâtir demain.",
  },
  {
    name: "BIO",
    title: "Biotechnologie et Agronomie",
    tag: "Sciences · Environnement",
    score: 78,
    color: "green",
    paths: 4,
    parcours: [
      "BIO (actif)",
      "IAA (fusionné)",
      "AEE (fusionné)",
      "PIP (fusionné)",
    ],
    parcoursDetails: {
      "BIO (actif)": {
        description:
          "Étude du vivant et valorisation des ressources biologiques.",
        matieres: "Biologie, microbiologie, biochimie",
        specificites: "Laboratoire, innovation et environnement",
      },
      "IAA (fusionné)": {
        description:
          "Ancien parcours dédié aux industries agricoles et alimentaires.",
        matieres: "Technologie alimentaire, hygiène, contrôle qualité",
        specificites: "Parcours historique fusionné avec BIO",
      },
      "AEE (fusionné)": {
        description:
          "Ancien parcours centré sur l'agriculture et l'environnement.",
        matieres: "Agronomie, écologie, gestion des ressources",
        specificites: "Parcours historique fusionné avec BIO",
      },
      "PIP (fusionné)": {
        description:
          "Ancien parcours consacré à la production et à l'innovation agricole.",
        matieres: "Production végétale, expérimentation, gestion agricole",
        specificites: "Parcours historique fusionné avec BIO",
      },
    },
    visual: "Laboratoire, cultures et environnement",
    desc: "Laboratoires, agriculture et innovation pour nourrir et préserver Madagascar.",
  },
  {
    name: "TOURISME",
    title: "Techniques du Tourisme",
    tag: "Hôtellerie · Voyage",
    score: 74,
    color: "teal",
    paths: 1,
    parcours: ["TEH"],
    parcoursDetails: {
      TEH: {
        description:
          "Accueil, hébergement et conception d'expériences touristiques.",
        matieres: "Communication, langues, gestion hôtelière",
        specificites: "Tourisme durable, patrimoine et relation client",
      },
    },
    visual: "Paysages, accueil et hôtellerie",
    desc: "Tourisme, environnement et hôtellerie au service d'une destination d'exception.",
  },
  {
    name: "AFFAIRES",
    title: "Techniques des Affaires",
    tag: "Finance · Management",
    score: 81,
    color: "navy",
    paths: 4,
    parcours: ["CAA", "DTJA", "EMP", "FIC"],
    parcoursDetails: {
      CAA: {
        description:
          "Gestion commerciale, relation client et développement des ventes.",
        matieres: "Marketing, commerce, communication",
        specificites: "Négociation et stratégie commerciale",
      },
      DTJA: {
        description:
          "Droit, administration et accompagnement des organisations.",
        matieres: "Droit, économie, administration",
        specificites: "Cadre juridique et gestion des activités",
      },
      EMP: {
        description: "Entrepreneuriat et management de projets et d'équipes.",
        matieres: "Management, entrepreneuriat, comptabilité",
        specificites: "Création d'activité et pilotage de projet",
      },
      FIC: {
        description:
          "Finance, comptabilité et contrôle de la performance des organisations.",
        matieres: "Comptabilité, finance, contrôle de gestion",
        specificites: "Analyse financière et aide à la décision",
      },
    },
    visual: "Graphiques, droit et réunions",
    desc: "Finance, droit, comptabilité et management pour piloter les organisations.",
  },
];

export const suggestions = [
  "Quelle formation correspond à mon profil ?",
  "Comparer ISAIA et IGGLIA",
  "Quels sont les débouchés en IA ?",
];
