# -*- coding: utf-8 -*-
import dataiku
import pandas as pd, numpy as np
from dataiku import pandasutils as pdu
from evaluate_llm import *

# Read recipe inputs
EMBEDDING_ID = "custom:iliad-plugin-conn-prod:text-embedding-ada-002"
LLM_ID = "custom:iliad-plugin-conn-prod:gpt-4o"
input_dataset = "input_data_chunked"
output_dataset = "input_data_response_evaluated"


def evaluate(LLM_ID, EMBEDDING_ID, input_dataset, output_dataset):
    # Initialize Dataiku and retrieve models
    initializer = DataikuInitializer()
    
    langchain_llm = initializer.get_langchain_llm(LLM_ID)
    custom_embeddings = initializer.get_custom_embeddings(EMBEDDING_ID)
    
    # Load and prepare documents
    doc_creator = DocumentCreator(input_dataset)
    df_sample = doc_creator.load_and_sample_documents(sample_size=100)
    documents, df_out = doc_creator.create_langchain_documents(df_sample)
    
    # Generate testset from documents
    testset_generator = TestsetGeneratorWrapper(langchain_llm, custom_embeddings)
    generated_dataset = testset_generator.generate_testset(documents, testset_size=50)
    df_generated = generated_dataset.to_pandas()
    print("Generated Testset:")
    print(df_generated)
    
    # Generate responses for each user input in the generated dataset
    response_generator = RAGResponseGenerator(langchain_llm)
    df_with_responses = response_generator.apply_responses_to_dataframe(df_generated)
    print("DataFrame with Responses:")
    print(df_with_responses.head())
    
    # Convert to EvaluationDataset for evaluation
    data_records = df_with_responses.to_dict("records")
    ragas_dataset = EvaluationDataset.from_list(data_records)
    
    # Evaluate the results
    evaluation_pipeline = EvaluationPipeline(langchain_llm, custom_embeddings)
    evaluation_results = evaluation_pipeline.evaluate(ragas_dataset)
    
    # Write evaluation results back to a Dataiku dataset
    ragas_evaluation = initializer.get_dataset(output_dataset)
    ragas_evaluation.write_with_schema(evaluation_results)

evaluate(LLM_ID, EMBEDDING_ID, input_dataset, output_dataset)