from index import run_index_pipeline
from generate import run_generate_pipeline
from evaluate import run_evaluation_pipeline


def main():
    print("Starting indexing...")
    document_store = run_index_pipeline()
    print("Indexing complete.")

    print("Starting query generation...")
    generated_results = run_generate_pipeline(document_store)
    print("Query generation complete.")
    run_evaluation_pipeline(generated_results)


if __name__ == "__main__":
    main()
