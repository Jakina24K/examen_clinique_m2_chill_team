from pathlib import Path
from rdflib import Graph

class RecommandationPromptService:
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
        """Extrait proprement les entités valides directement depuis le graphe SPARQL."""
        if len(self.graph) == 0:
            self.load_ontology()

        # Requête ciblée sur les individus réels (instances des classes)
        query = f"""
        PREFIX : <{self.prefix}>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>

        SELECT DISTINCT ?ind ?type WHERE {{
            ?ind rdf:type ?type .
            FILTER(?type != owl:NamedIndividual)
            FILTER(STRSTARTS(STR(?ind), "{self.prefix}"))
        }}
        """
        results = self.graph.query(query)
        
        competences = set()
        interets = set()

        for row in results:
            name = str(row.ind).split("#")[-1].split("/")[-1]
            type_name = str(row.type).split("#")[-1].split("/")[-1]

            # Séparation basée sur la classe RDF (Adaptez 'Competence' et 'CentreInteret' selon votre TTL)
            if "competence" in type_name.lower():
                competences.add(name)
            elif "parcours" not in type_name.lower():
                interets.add(name)

        # Fallback au cas où aucune classe spécifique n'est identifiée
        all_concepts = list(competences | interets)
        return {
            "centres_interet": list(interets) if interets else all_concepts,
            "competences": list(competences) if competences else all_concepts
        }

    def get_recommandation_dynamique(
        self, competences: list[str] = None, centres_interet: list[str] = None
    ) -> list[dict]:
        """Retourne les parcours triés par nombre de correspondances (score)."""
        if len(self.graph) == 0:
            self.load_ontology()

        clean_cp = competences or []
        clean_ci = centres_interet or []

        if not clean_cp and not clean_ci:
            return []

        matches_uris = " ".join([f"<{self.prefix}{item}>" for item in set(clean_cp + clean_ci)])

        query = f"""
        PREFIX : <{self.prefix}>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

        SELECT ?parcours (SAMPLE(?desc) AS ?description) (COUNT(DISTINCT ?match) AS ?score) WHERE {{
            ?parcours rdf:type :parcours .
            ?parcours ?p ?match .
            VALUES ?match {{ {matches_uris} }}
            OPTIONAL {{ ?parcours :descriptionParcours ?desc . }}
        }}
        GROUP BY ?parcours
        ORDER BY DESC(?score)
        """

        results = self.graph.query(query)
        recommandations = []

        for row in results:
            parcours_name = str(row.parcours).split("#")[-1].split("/")[-1]
            recommandations.append({
                "parcours": parcours_name,
                "descriptionParcours": str(row.description) if row.description else None,
                "score": int(row.score)
            })

        return recommandations


recommandation_prompt_service = RecommandationPromptService()