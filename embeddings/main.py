import argparse
from pathlib import Path
import sys
from embeddings import preprocess_manuals, create_vector_db

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RAG para manuales en PDF")
    parser.add_argument(
        "-p",
        "--manuals_path",
        type=str,
        default="./manuals",
        help="Ruta a la carpeta que contiene los manuales en PDF.",
    )
    parser.add_argument(
        "-e",
        "--create-embeddings",
        action="store_true",
        help="Indica si se deben crear los embeddings y la base de datos vectorial.",
    )

    args = parser.parse_args()

    if args.create_embeddings:
        if not args.manuals_path:
            print("No se indico la ruta a los manuales.")
            print("\nUso: python main.py -m <folder_con_pdfs>")
            sys.exit(1)

        if not Path(args.manuals_path).exists():
            print(f"ERROR: No existe: {args.manuals_path}")
            print("\nUso: python main.py -m <folder_con_pdfs>")
            sys.exit(1)

        docs = preprocess_manuals(args.manuals_path)

        vectordb = create_vector_db(docs)
