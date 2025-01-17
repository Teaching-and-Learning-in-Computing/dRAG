from haystack import Pipeline
from haystack.components.builders import AnswerBuilder, ChatPromptBuilder
from haystack.components.joiners.document_joiner import DocumentJoiner
from haystack.components.rankers import TransformersSimilarityRanker
from haystack.components.retrievers.in_memory import (
    InMemoryBM25Retriever,
    InMemoryEmbeddingRetriever,
)
from haystack.dataclasses import ChatMessage
from haystack.utils import ComponentDevice
from haystack_integrations.components.embedders.ollama import OllamaTextEmbedder
from haystack_integrations.components.generators.ollama import OllamaChatGenerator

from prompts import system_prompt
from utils.serializing import read_input_json, serialize_generated_answer

device = ComponentDevice.resolve_device()


def run_generate_pipeline(document_store):
    """
    Executes the generate pipeline to process queries and generate answers
      based on the provided document store and input json file.

    The pipeline components include:
        - OllamaTextEmbedder: Generates embeddings for the input query.
        - InMemoryEmbeddingRetriever: Retrieves documents based on the query embeddings.
        - InMemoryBM25Retriever: Retrieves documents using BM25 for term-based ranking.
        - DocumentJoiner: Combines documents from multiple retrievers.
        - TransformersSimilarityRanker: Ranks documents based on semantic similarity.
        - ChatPromptBuilder: Builds a chat prompt using the query and ranked documents.
        - OllamaChatGenerator: Generates responses using a specified LLM model.
        - AnswerBuilder: Compiles the generated answer along with supporting documents.

    Args:
        document_store (DocumentStore): An instance of a Haystack document store containing indexed documents.

    Returns:
        str: A JSON-serialized string containing the ground truth answers and generated answers for each query.
    """
    system_message = ChatMessage.from_system(system_prompt)
    user_message = ChatMessage.from_user("Query: {{query}}\n\n Answer: ")
    chat_template = [system_message, user_message]

    generate = Pipeline()
    generate.add_component(
        "text_embedder",
        OllamaTextEmbedder(
            model="snowflake-arctic-embed2",  # we can probably go smaller
            generation_kwargs={
                "num_ctx": 8192
            },  # Ollama has a bug where if no ctx is specified, it sets it to a small default
        ),
    )
    generate.add_component(
        "embedding_retriever", InMemoryEmbeddingRetriever(document_store)
    )
    generate.add_component("bm25_retriever", InMemoryBM25Retriever(document_store))
    generate.add_component("document_joiner", DocumentJoiner())
    generate.add_component(
        "ranker",
        TransformersSimilarityRanker(
            model="BAAI/bge-reranker-v2-m3",  # switching this to OllamaRanker (or whatever it will be called) would be better
            device=device,
            top_k=3,  # we can make this larger if we believe the LLM can handle it
        ),
    )
    generate.add_component(
        "prompt_builder",
        ChatPromptBuilder(
            template=chat_template, required_variables=["query", "documents"]
        ),
    )
    generate.add_component(
        "llm",
        OllamaChatGenerator(
            model="qwen2.5:latest",  # biggest variable here, we should try different models
            generation_kwargs={"seed": 42},
        ),
    )
    generate.add_component("answer_builder", AnswerBuilder())

    generate.connect("text_embedder.embedding", "embedding_retriever.query_embedding")
    generate.connect("embedding_retriever.documents", "document_joiner.documents")
    generate.connect("bm25_retriever.documents", "document_joiner.documents")
    generate.connect("document_joiner.documents", "ranker.documents")
    generate.connect("ranker.documents", "prompt_builder.documents")
    generate.connect("ranker.documents", "answer_builder.documents")
    generate.connect("prompt_builder.prompt", "llm.messages")
    generate.connect("llm.replies", "answer_builder.replies")

    generate.draw("visual_design/generate_pipeline.png")

    prompts = read_input_json("documents/input/input.json")
    results = []
    for prompt_dict in prompts:
        query = prompt_dict.get("question", "")
        answer = prompt_dict.get("answer", "")
        result = generate.run(
            {
                "text_embedder": {"text": query},
                "bm25_retriever": {"query": query},
                "ranker": {"query": query},
                "prompt_builder": {"query": query},
                "answer_builder": {"query": query},
            }
        )
        results_with_original = {"answer": answer, "generated_answer": result}
        results.append(results_with_original)

    return serialize_generated_answer(results)
