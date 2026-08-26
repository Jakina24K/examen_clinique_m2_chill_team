from pathlib import Path
from rdflib import Graph


class recommandation_prompt_service:
    def __init__(self):
        self.graph = Graph()
        self.prefix = "http://www.semanticweb.org/oracle/ontologies/2026/7/untitled-ontology-14/"
        self.load_ontology()

    def load_ontology(self, file_path: str = None):
        """Charge le fichier OrientIA.ttl."""
        if file_path is None:
            base_dir = Path(__file__).resolve().parent.parent
            file_path = base_dir / "ontology" / "OrientIA.ttl"

            if not file_path.exists():
                file_path = base_dir.parent / "OrientIA.ttl"

        if not file_path.exists():
            raise FileNotFoundError(f"Fichier ontologie introuvable : {file_path}")

        self.graph.parse(str(file_path), format="turtle")
        print(f"🟢 [RDFLIB] Ontologie chargée ! Total triplets : {len(self.graph)}", flush=True)

    def get_all_concepts(self) -> dict:
        """Extrait uniquement les VRAIS individus autorisés (exclut les propriétés et métadonnées RDF)."""
        if len(self.graph) == 0:
            self.load_ontology()

        # Liste de mots à exclure impérativement (propriétés / classes méta)
        banned_words = [
            "competences", "aPourCentreInteret", "centreInterets", "developpe",
            "etreRequisePour", "possede", "parcours", "NamedIndividual", "Class",
            "Ontology", "descriptionParcours", "http", "owl", "rdf", "rdfs"
        ]

        query = """
        SELECT DISTINCT ?concept WHERE {
            ?concept ?p ?o .
        }
        """
        results = self.graph.query(query)
        concepts_set = set()

        for row in results:
            name = str(row.concept).split("/")[-1].split("#")[-1]
            if name not in banned_words and not name.startswith("http"):
                concepts_set.add(name)

        # Tri basique
        competences = [c for c in concepts_set if c.startswith("CP_") or "competence" in c.lower()]
        interets = [c for c in concepts_set if c not in competences]

        # Si pas de préfixe explicite CP_, on fournit la liste complète
        if not competences:
            competences = list(concepts_set)
        if not interets:
            interets = list(concepts_set)

        return {
            "centres_interet": list(set(interets)),
            "competences": list(set(competences))
        }

    def get_recommandation_dynamique(
        self, competences: list[str] = None, centres_interet: list[str] = None
    ) -> list[dict]:
        """Retourne UNIQUEMENT les entités de type :parcours qui correspondent aux critères."""
        if len(self.graph) == 0:
            self.load_ontology()

        competences = competences or []
        centres_interet = centres_interet or []

        # Exclut tout mot parasite s'il s'est glissé dans les listes
        banned = {"competences", "aPourCentreInteret", "centreInterets", "developpe", "possede"}
        clean_cp = [c for c in competences if c not in banned]
        clean_ci = [c for c in centres_interet if c not in banned]

        if not clean_cp and not clean_ci:
            return []

        matches = " ".join([f":{item}" for item in set(clean_cp + clean_ci)])

        query = f"""
        PREFIX : <{self.prefix}>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

        SELECT DISTINCT ?parcours ?descriptionParcours WHERE {{
            ?parcours rdf:type :parcours .
            ?parcours ?p ?match .
            VALUES ?match {{ {matches} }}
            OPTIONAL {{ ?parcours :descriptionParcours ?descriptionParcours . }}
        }}
        """

        results = self.graph.query(query)
        recommandations = []

        for row in results:
            parcours_name = str(row.parcours).split("/")[-1].split("#")[-1]
            if parcours_name not in banned:
                recommandations.append({
                    "parcours": parcours_name,
                    "descriptionParcours": str(row.descriptionParcours) if row.descriptionParcours else None,
                })

        return recommandations


recommandation_prompt_service = recommandation_prompt_service()