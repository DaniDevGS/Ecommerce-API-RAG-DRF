import os
from upstash_vector import Index
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("UPSTASH_VECTOR_REST_URL", "").strip().replace('"', '').replace("'", "")
token = os.getenv("UPSTASH_VECTOR_REST_TOKEN", "").strip().replace('"', '').replace("'", "")

if not url or not token:
    print("Advertencia: No se encontraron las credenciales de Upstash Vector en el entorno (revisa el .env).")

index = Index(url=url, token=token)

def indexar_productos(productos):
    if not url or not token:
        return
        
    vectors = []
    for p in productos:
        metadata_text = (
            f"Producto: {p.nombre}. "
            f"Descripción: {p.descripcion}. "
            f"Características: {p.caracteristicas}. "
            f"Categoría: {p.subcategoria.nombre if p.subcategoria else 'N/A'}"
            f"Cantidad: {p.cantidad}"
        )
        
        metadata = {
            "id": p.id,
            "nombre": p.nombre,
            "precio": float(p.precio) if p.precio else 0.0,
            "categoria": p.subcategoria.nombre if p.subcategoria else "N/A",
            "cantidad": p.cantidad
        }
        vectors.append((str(p.id), metadata_text, metadata))
    
    if vectors:
        index.upsert(vectors=vectors)

def buscar_productos_similares(query, top_k=5):
    if not url or not token:
        return []
        
    try:
        resultados = index.query(data=query, top_k=top_k, include_metadata=True, include_data=True)
        return resultados
    except Exception as e:
        print(f"Error querying Upstash: {e}")
        return []
