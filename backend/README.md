# ETUDE DE CAS M2 (IGGLIA 5) - ORIENT'IA 

**- RANDRIANANDRAINA Jessica , N°02**
**- RAJOHNSON Fitia , N°04**
**- LAZAHARIVELO Jakina Andriantsoa , N° 05**
**- ANDRIANIRINA Tsanta Fitiavana , N°08**
**- RAMANDIMBISON Ezra Niel , N°15**
**- ANDRITIANA FANORENANTSOA Steddi Karen , N°48**
**- RANDRIANAVALONA Mahefa Nirina , N°55**

## Stack Technique
- **LLM**: gemini-2.5-flash
- **Backend API**: FastAPI / Uvicorn
- **Validation Data**: Pydantic v2
- **RAG & Vector Store**: ChromaDB
- **Sécurité**: Garde-fous Regex & Analyse Contextuelle

## Lancement Rapide

1. **Installer les dépendances :**
```bash
cd backend
python -m venv .venv   
.venv\Scripts\activate   
python.exe -m pip install --upgrade pip
pip install -r requirements.txt
```
# Assurez-vous que les valeurs du fichier « .env » sont à jour pour votre environnement.

2. **Migration & config bd :**
```bash
alembic revision --autogenerate -m "initial_migration"
alembic upgrade head
```
3. **Demarrarer le serveur :**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000    
``` 
4. **Ingestion :**
```bash
python -m app.rag.ingest
``` 
5. **Test :**
```bash
pytest -v
``` 
6. **Màj requirements.txt :**
```bash
pip freeze > requirements.txt  
``` 