"""
Script de test simple pour vérifier que les importations fonctionnent.
"""
import sys
import os

print("Test des importations...")

# Test depuis camera_system
print("\n1. Test depuis camera_system:")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from vector_db import LocalVectorDB
    print("✅ vector_db importé")
    
    from pipeline import FacePipeline
    print("✅ pipeline importé")
    
    # Vérifier que les méthodes existent
    pipeline = FacePipeline.__new__(FacePipeline)  # Créer une instance sans __init__
    if hasattr(pipeline, 'get_embeddings_from_multiple_paths'):
        print("✅ get_embeddings_from_multiple_paths existe")
    else:
        print("❌ get_embeddings_from_multiple_paths MANQUE")
    
    db = LocalVectorDB.__new__(LocalVectorDB)
    if hasattr(db, 'register_student'):
        print("✅ register_student existe")
    else:
        print("❌ register_student MANQUE")
        
except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()

# Test depuis la racine
print("\n2. Test depuis la racine:")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    import importlib
    import vector_db as vector_db_root
    print("✅ vector_db (racine) importé")
    
    import pipeline as pipeline_root
    print("✅ pipeline (racine) importé")
    
    # Vérifier que les méthodes existent
    pipeline_root_class = pipeline_root.FacePipeline.__new__(pipeline_root.FacePipeline)
    if hasattr(pipeline_root_class, 'get_embeddings_from_multiple_paths'):
        print("✅ get_embeddings_from_multiple_paths existe (racine)")
    else:
        print("❌ get_embeddings_from_multiple_paths MANQUE (racine)")
    
    db_root = vector_db_root.LocalVectorDB.__new__(vector_db_root.LocalVectorDB)
    if hasattr(db_root, 'register_student'):
        print("✅ register_student existe (racine)")
    else:
        print("❌ register_student MANQUE (racine)")
        
except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()

print("\nTest terminé.")