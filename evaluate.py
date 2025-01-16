from haystack.components.evaluators import FaithfulnessEvaluator
from haystack.utils.auth import Secret

from utils.serializing import (
    read_serialized_generated_answer,
    serialize_evaluation_results,
)


def run_evaluation_pipeline(file_path):
    queries, documents, answers, _ = read_serialized_generated_answer(
        file_path
    )

    evaluator = FaithfulnessEvaluator(
        api_key=Secret.from_token("test-api-key"),
        api_params={
            "api_base_url": "http://localhost:11434/v1",
            "model": "qwen2.5:latest",
        },
    )

    all_results = []

    for query, document, answer in zip(queries, documents, answers):
        try:
            result = evaluator.run(
                questions=[query], contexts=[document], predicted_answers=[answer]
            )
            all_results.append(result)
        except ValueError as e:
            print(f"Skipping due to error: {e}")
            continue

    serialize_evaluation_results(all_results)
