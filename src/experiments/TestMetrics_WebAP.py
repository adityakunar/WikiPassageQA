import pandas as pd
import os
import numpy as np


class TestMetrics_WebAP:

    def __init__(self, testpath):
        if testpath.endswith("tsv"):
            test = pd.read_csv(testpath, sep='\t')
        else:
            test = pd.read_csv(testpath)
        test = test.rename(columns={"RelevantPassages":"PassageID", "DocumentID": "DocID"})
        #   QID                                           Question  DocumentID DocumentName PassageID
        #0  449  What is Iraq's role in political unstabilization?         543    Iraq.html     42,43

        test_true = test
        print(test_true)

        # convert char Passage Ids to int
        test_true["PassageID"] = test_true["PassageID"].astype(int)
        print(test_true)

        self.test = test_true


    def get_metrics(self, new_results, max_results):
        # new results have the the columns [QID, DocID, PassageID]

        prec_5, recall_5 = self.precision_recall(new_results, max_records = 5)
        prec_10, recall_10 = self.precision_recall(new_results, max_records = 10)
        MRR = self.calc_MRR(new_results)
        MAP = self.calc_MAP(new_results)

        print("METRICS:")
        print("Precis@5 = " +str(prec_5))
        print("Recall@5 = " +str(recall_5))

        print("Precis@10 = " +str(prec_10))
        print("Recall@10 = " +str(recall_10))

        print("MRR = " +str(MRR))
        print("MAP = " +str(MAP))


    def precision_recall(self, new_results, max_records):
        # group by QID
        qids = self.test["QID"].unique()
        prec = [] 
        recall = []
        # count total entries in true
        for qid in qids:
            true = self.test[self.test.QID == qid]
            true["key"] = true["DocID"].astype(str) +" | "+  true["PassageID"].astype(str)
            pred = new_results[new_results.QID == qid]
            pred["key"] = pred["DocID"].astype(str) +" | "+ pred["PassageID"].astype(str)

            presence = true["key"].isin(pred["key"].head(max_records)).values
            TP = presence.sum()
            FN = (~presence).sum()

            prec.append(TP/ len(pred["key"].values))
            recall.append(TP/ len(true["key"].values))

        return np.mean(prec), np.mean(recall)
        # Compare presence of entries in new_entries
    
    def calc_MAP(self,new_results):
        # group by QID
        qids = self.test["QID"].unique()
        
        overall_APs = []
        for qid in qids:
            true = self.test[self.test.QID == qid]
            true["key"] = true["DocID"].astype(str) +" | "+  true["PassageID"].astype(str)
            pred = new_results[new_results.QID == qid]
            pred["key"] = pred["DocID"].astype(str) +" | "+ pred["PassageID"].astype(str)

            presence = pred["key"].isin(true["key"]).values

            APs = []
            for rank in range(1,len(presence) +1 ):
                # rank starting with 0
                if presence[rank-1] == True:
                    APs.append((len(APs)+1)/rank)
            if len(APs) > 0:
                overall_APs.append(np.sum(APs) / len(APs))
        
        MAP = np.sum(overall_APs) / len(qids)
        return MAP


    def calc_MRR(self, new_results):
        # group by QID
        qids = self.test["QID"].unique()
        
        first_occur_reci = [] 
        for qid in qids:
            true = self.test[self.test.QID == qid]
            true["key"] = true["DocID"].astype(str) +" | "+  true["PassageID"].astype(str)
            pred = new_results[new_results.QID == qid]
            pred["key"] = pred["DocID"].astype(str) +" | "+ pred["PassageID"].astype(str)

            presence = pred["key"].isin(true["key"])

            ranks = np.where(presence == True)[0]
            if len(ranks) == 0:
                continue
            # rank starting with 0
            s = 1/(ranks[0] + 1)
            first_occur_reci.append(s)

        MRR = np.sum(first_occur_reci) / len(qids)
        return MRR
        

if __name__ == "__main__":
    CUR_DIR = os.path.dirname(__file__)
    testpath = os.path.join(CUR_DIR, '../../data/raw/WikiPassageQA/test.tsv')

    tester = TestMetrics(testpath)
