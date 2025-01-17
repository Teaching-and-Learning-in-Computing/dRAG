from haystack import Pipeline
from haystack.components.converters import PDFMinerToDocument
from haystack.components.preprocessors import DocumentCleaner, DocumentSplitter
from haystack.components.writers import DocumentWriter
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack_integrations.components.embedders.ollama import OllamaDocumentEmbedder


def run_index_pipeline():
    """
    Executes the index pipeline to preprocess, embed, and store PDF documents in an in-memory document store.

    The pipeline components include:
        - PDFMinerToDocument: Converts PDF files into text-based documents.
        - DocumentCleaner: Cleans and preprocesses document text.
        - DocumentSplitter: Splits large documents into smaller chunks.
        - OllamaDocumentEmbedder: Embeds the document chunks using a specified model.
        - DocumentWriter: Stores the processed and embedded documents.

    Returns:
        InMemoryDocumentStore: A document store containing the processed and embedded documents.
    """
    document_store = InMemoryDocumentStore()
    index_pipeline = Pipeline()
    index_pipeline.add_component("pdf_converter", PDFMinerToDocument())
    index_pipeline.add_component("document_cleaner", DocumentCleaner())
    index_pipeline.add_component(
        "document_splitter", DocumentSplitter()
    )  # currently splitting with default values
    index_pipeline.add_component(
        "document_embedder",
        OllamaDocumentEmbedder(
            model="snowflake-arctic-embed2"
        ),  # same model as TextEmbedder in generate
    )
    index_pipeline.add_component("document_writer", DocumentWriter(document_store))

    index_pipeline.connect("pdf_converter.documents", "document_cleaner.documents")
    index_pipeline.connect("document_cleaner.documents", "document_splitter.documents")
    index_pipeline.connect("document_splitter.documents", "document_embedder.documents")
    index_pipeline.connect("document_embedder.documents", "document_writer.documents")

    index_pipeline.run(
        {"pdf_converter": {"sources": ["documents/source_documents/test.pdf"]}}
    )
    return document_store
