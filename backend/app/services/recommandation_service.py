from pathlib import Path
from rdflib import Graph, URIRef

class recommandation_service:
    def __init__(self):
        self.graph = Graph()
        self.prefix = "http://www.semanticweb.org/oracle/ontologies/2026/7/untitled-ontology-14/"

    def load_ontology(self, file_path: str = None):
        if file_path is None:
            base_dir = Path(__file__).resolve().parent.parent
            file_path = base_dir / "ontology" / "OrientIA.ttl"
        self.graph.parse(str(file_path), format="turtle")

    def get_recommandation_dynamique(
        self, 
        competences: list[str], 
        centres_interet: list[str] = None, 
        matieres_pref: list[str] = None
    ) -> list[dict]:
        """
        Recommande des parcours dynamiquement en fonction des compétences transmises
        sans avoir besoin d'un étudiant pré-enregistré dans l'ontologie.
        """
        if not competences:
            return []

        # Formater les compétences sous forme d'URIs SPARQL : :CP1, :CP2...
        cp_uris = " ".join([f":{cp}" for cp in competences])

        query = f"""
        PREFIX : <{self.prefix}>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

        SELECT DISTINCT
            ?parcours
            ?descriptionParcours
            (COUNT(DISTINCT ?cp) AS ?nbCompetencesCorrespondantes)
        WHERE {{
            ?parcours rdf:type :parcours .
            OPTIONAL {{ ?parcours :descriptionParcours ?descriptionParcours . }}

            # Le parcours doit développer au moins une des compétences soumises
            ?parcours :developpe ?cp .
            VALUES ?cp {{ {cp_uris} }}
        }}
        GROUP BY ?parcours ?descriptionParcours
        ORDER BY DESC(?nbCompetencesCorrespondantes)
        """

        results = self.graph.query(query)
        recommandations = []

        for row in results:
            recommandations.append({
                "parcours": str(row.parcours).split("/")[-1], # Extrait le nom court
                "descriptionParcours": str(row.descriptionParcours) if row.descriptionParcours else None,
                "scoreCorrespondance": int(row.nbCompetencesCorrespondantes),
                "centresInteretFournis": centres_interet or [],
                "matieresPrefereesFournies": matieres_pref or []
            })

        return recommandations

recommandation_service = recommandation_service()