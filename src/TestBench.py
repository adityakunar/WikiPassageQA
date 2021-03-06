from experiments.TestMetrics_WikiQA import TestMetrics_WikiQA
from experiments.TestMetrics_WebAP import TestMetrics_WebAP
import os
from models.tf_idf_vsm import tf_idf_VSM
import pandas as pd
from feature_extraction.passage_feature_extraction import PassageFeatureExtraction
from models.query_likelihood import QueryLikelihood
import json
import ast


def vsm_WikiQA(dataset_name, test_csv_path, passages_path, max_results):
    CUR_DIR = os.path.dirname(__file__)
    DATA_DIR = os.path.join(CUR_DIR, "../data")
    PROCESSED_DATA_DIR = os.path.join(DATA_DIR, "processed")

    if dataset_name not in ["WebAP", "WikiQA"]:
        print("dataset_name not in [\"WebAP\", \"WikiQA\"]")
        exit(1)
        return

    test_results_file = PROCESSED_DATA_DIR+"/vsm_test_results_"+ dataset_name +".csv"
    if os.path.exists(test_results_file):
        test_result = pd.read_csv(test_results_file)
        return test_result

    if test_csv_path.endswith("tsv"):
        test = pd.read_csv(test_csv_path, sep='\t')
    else:
        test = pd.read_csv(test_csv_path)

    model = tf_idf_VSM(passages_path)
    columns = ["QID", "DocID", "PassageID", "cosine_sim"]
    test_result = pd.DataFrame(columns=columns)

    unique_query_df = test[["QID", "Question"]].drop_duplicates()
    length = unique_query_df.shape[0]
    for i in range(length):
        query = test.iloc[i, 1]
        if dataset_name.endswith("WebAP"):
            query = test.iloc[i, 2]
        result = model.get_ranked_passages(query, max_results = max_results)
        #       DocId  PassageId                                            Passage  cosine_sim
        # 12449    140          0  Proto-Slavic is defined as the last stage of t...    0.399138
        for j in range(result.shape[0]):
            df2 = pd.DataFrame([[ test.iloc[i,0], result.iloc[j,0], result.iloc[j,1], result.iloc[j,3] ]], columns=columns)
            test_result = test_result.append(df2)
        print("vsm: " + str(i) + "/" + str(length))

    test_result.to_csv(test_results_file, index=False)

    return test_result


def vsm_WebAP(dataset_name, test_csv_path, passages_path, max_results):
    CUR_DIR = os.path.dirname(__file__)
    DATA_DIR = os.path.join(CUR_DIR, "../data")
    PROCESSED_DATA_DIR = os.path.join(DATA_DIR, "processed")

    if dataset_name not in ["WebAP", "WikiQA"]:
        print("dataset_name not in [\"WebAP\", \"WikiQA\"]")
        exit(1)
        return

    test_results_file = PROCESSED_DATA_DIR+"/vsm_test_results_"+ dataset_name +".csv"
    if os.path.exists(test_results_file):
        test_result = pd.read_csv(test_results_file)
        return test_result

    if test_csv_path.endswith("tsv"):
        test = pd.read_csv(test_csv_path, sep='\t')
    else:
        test = pd.read_csv(test_csv_path)


    model = tf_idf_VSM(passages_path)
    columns = ["QID", "DocID", "PassageID", "cosine_sim"]
    test_result = pd.DataFrame(columns=columns)

    unique_query_df = test[['QID','Question']].drop_duplicates()
    length = unique_query_df.shape[0]
    for i in range(length):
        query = unique_query_df.iloc[i, 1]
        if dataset_name.endswith("WebAP"):
            query = unique_query_df.iloc[i, 1]
        result = model.get_ranked_passages(query, max_results = max_results)
        #       DocId  PassageId                                            Passage  cosine_sim
        #12449    140          0  Proto-Slavic is defined as the last stage of t...    0.399138
        for j in range(result.shape[0]):
            df2 = pd.DataFrame([[ unique_query_df.iloc[i,0], result.iloc[j,0], result.iloc[j,1], result.iloc[j,3] ]], columns=columns)
            test_result = test_result.append(df2)
        print("vsm: " + str(i) +"/"+str(length))

    test_result.to_csv(test_results_file, index=False)

    return test_result

def ql_webap(max_results):
    CUR_DIR = os.path.dirname(__file__)
    DATA_DIR = os.path.join(CUR_DIR, "../data")
    EXTRACT_DATA_DIR = os.path.join(DATA_DIR, "extracted")
    PROCESSED_DATA_DIR = os.path.join(DATA_DIR, "processed")

    passage_data_path = os.path.join(EXTRACT_DATA_DIR, "webap_passages.json")
    fe = PassageFeatureExtraction(passage_data_path)
    passage_data = fe.passage_data

    query_path = os.path.join(EXTRACT_DATA_DIR, "webap_queries.csv")
    query_df = pd.read_csv(query_path)

    # fe.extract_features(PROCESSED_DATA_DIR)
    # doc_term_freq = fe.doc_term_freq
    # col_term_freq = fe.col_term_freq
    doc_term_freq = json.load(
        open(os.path.join(PROCESSED_DATA_DIR, "doc_term_freq_webap.json"), "r")
    )
    col_term_freq = json.load(
        open(os.path.join(PROCESSED_DATA_DIR, "col_term_freq_webap.json"), "r")
    )
    ql = QueryLikelihood(passage_data, doc_term_freq, col_term_freq, smoothing="JM")
    queries = [ast.literal_eval(el) for el in query_df["Question"].tolist()]
    qids = query_df["QID"].tolist()
    ql.fit(queries)

    scores = ql.predict(max_results=max_results)
    score_dfs = []
    for i, (score, qid) in enumerate(zip(scores, qids)):
        for j, record in enumerate(score):
            scores[i][j]["QID"] = qid
        score_dfs.append(pd.DataFrame.from_records(scores[i]))
    score_df = pd.concat(score_dfs)
    score_df.to_csv(os.path.join(PROCESSED_DATA_DIR, "ql_scores_webap2.csv"))
    return score_df


def ql_wikiqa(max_results):
    CUR_DIR = os.path.dirname(__file__)
    DATA_DIR = os.path.join(CUR_DIR, "../../data")
    EXTRACT_DATA_DIR = os.path.join(DATA_DIR, "extracted")
    PROCESSED_DATA_DIR = os.path.join(DATA_DIR, "processed")

    passage_data_path = os.path.join(EXTRACT_DATA_DIR, "document_passages.json")
    fe = PassageFeatureExtraction(passage_data_path)
    passage_data = fe.passage_data

    query_path = os.path.join(EXTRACT_DATA_DIR, "test.csv")
    query_df = pd.read_csv(query_path)

    # fe.extract_features(PROCESSED_DATA_DIR)
    # doc_term_freq = fe.doc_term_freq
    # col_term_freq = fe.col_term_freq
    doc_term_freq = json.load(
        open(os.path.join(PROCESSED_DATA_DIR, "doc_term_freq.json"), "r")
    )
    col_term_freq = json.load(
        open(os.path.join(PROCESSED_DATA_DIR, "col_term_freq.json"), "r")
    )
    ql = QueryLikelihood(passage_data, doc_term_freq, col_term_freq, smoothing="JM")
    queries = [ast.literal_eval(el) for el in query_df["Question"].tolist()]
    qids = query_df["QID"].tolist()
    ql.fit(queries)

    scores = ql.predict(max_results=max_results)
    score_dfs = []
    for i, (score, qid) in enumerate(zip(scores, qids)):
        for j, record in enumerate(score):
            scores[i][j]["QID"] = qid
        score_dfs.append(pd.DataFrame.from_records(scores[i]))
    score_df = pd.concat(score_dfs)
    score_df.to_csv(os.path.join(PROCESSED_DATA_DIR, "ql_scores_wikiqa.csv"))
    return score_df

if __name__ == "__main__":
    CUR_DIR = os.path.dirname(__file__)
    PROCESSED_DATA_DIR = os.path.join("./data/processed")
    
    # WikiPassageQA
    test_csv_path = './data/raw/WikiPassageQA/test.tsv'
    passages_path = PROCESSED_DATA_DIR+'/passage_df_WikiQA.csv'
    tester = TestMetrics_WikiQA(test_csv_path)
    max_results = 20

    vsm_results = vsm_WikiQA("WikiQA", test_csv_path, passages_path, max_results)
    tester.get_metrics(vsm_results, max_results)

    ql_results_wikiqa = ql_wikiqa(max_results)
    tester_wikiqa.get_metrics(ql_results_wikiqa, 20)

    # WebAP
    test_csv_path = './data/extracted/webap_queries.csv'
    passages_path = PROCESSED_DATA_DIR+'/passage_df_WebAP.csv'
    tester = TestMetrics_WebAP(test_csv_path)
    max_results = 1000

    vsm_results = vsm_WebAP("WebAP", test_csv_path, passages_path, max_results)
    tester.get_metrics(vsm_results, max_results)

    ql_results_webap = ql_webap(max_results)
    tester_webap.get_metrics(ql_results_webap, max_results)
