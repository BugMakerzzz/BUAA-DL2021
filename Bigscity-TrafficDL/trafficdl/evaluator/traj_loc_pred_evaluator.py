import os
import json
import time

from trafficdl.evaluator.abstract_evaluator import AbstractEvaluator
from trafficdl.evaluator.eval_funcs import top_k
allowed_metrics = ['Precision', 'Recall', 'F1', 'MRR', 'MAP', 'NDCG']


class TrajLocPredEvaluator(AbstractEvaluator):

    def __init__(self, config):
        self.metrics = config['metrics']  # 评估指标, 是一个 list
        self.config = config
        self.topk = config['topk']
        self.result = {}
        self.intermediate_result = {
            'total': 0,
            'hit': 0,
            'rank': 0.0,
            'dcg': 0.0
        }
        self.intermediate_result5 = {
            'total': 0,
            'hit': 0,
            'rank': 0.0,
            'dcg': 0.0
        }
        self.intermediate_result10 = {
            'total': 0,
            'hit': 0,
            'rank': 0.0,
            'dcg': 0.0
        }
        self.intermediate_result100 = {
            'total': 0,
            'hit': 0,
            'rank': 0.0,
            'dcg': 0.0
        }
        self.intermediate_result1000 = {
            'total': 0,
            'hit': 0,
            'rank': 0.0,
            'dcg': 0.0
        }
        self._check_config()

    def _check_config(self):
        if not isinstance(self.metrics, list):
            raise TypeError('Evaluator type is not list')
        for i in self.metrics:
            if i not in allowed_metrics:
                raise ValueError('the metric is not allowed in \
                    TrajLocPredEvaluator')

    def collect(self, batch):
        """
        Args:
            batch (dict): contains three keys: uid, loc_true, and loc_pred.
            uid (list): 来自于 batch 中的 uid，通过索引可以确定 loc_true 与 loc_pred
                中每一行（元素）是哪个用户的一次输入。
            loc_true (list): 期望地点(target)，来自于 batch 中的 target
            loc_pred (matrix): 实际上模型的输出，batch_size * output_dim.
        """
        if not isinstance(batch, dict):
            raise TypeError('evaluator.collect input is not a dict of user')
        hit, rank, dcg = top_k(batch['loc_pred'], batch['loc_true'], self.topk)
        total = len(batch['loc_true'])
        self.intermediate_result['total'] += total
        self.intermediate_result['hit'] += hit
        self.intermediate_result['rank'] += rank
        self.intermediate_result['dcg'] += dcg

        hit, rank, dcg = top_k(batch['loc_pred'], batch['loc_true'], 5)
        total = len(batch['loc_true'])
        self.intermediate_result5['total'] += total
        self.intermediate_result5['hit'] += hit
        self.intermediate_result5['rank'] += rank
        self.intermediate_result5['dcg'] += dcg

        hit, rank, dcg = top_k(batch['loc_pred'], batch['loc_true'], 10)
        total = len(batch['loc_true'])
        self.intermediate_result10['total'] += total
        self.intermediate_result10['hit'] += hit
        self.intermediate_result10['rank'] += rank
        self.intermediate_result10['dcg'] += dcg

        hit, rank, dcg = top_k(batch['loc_pred'], batch['loc_true'], 100)
        total = len(batch['loc_true'])
        self.intermediate_result100['total'] += total
        self.intermediate_result100['hit'] += hit
        self.intermediate_result100['rank'] += rank
        self.intermediate_result100['dcg'] += dcg

        hit, rank, dcg = top_k(batch['loc_pred'], batch['loc_true'], 1000)
        total = len(batch['loc_true'])
        self.intermediate_result1000['total'] += total
        self.intermediate_result1000['hit'] += hit
        self.intermediate_result1000['rank'] += rank
        self.intermediate_result1000['dcg'] += dcg

    def evaluate(self):
        precision_key = 'Precision@{}'.format(self.topk)
        precision_key5 = 'Precision@{}'.format(5)
        precision_key10 = 'Precision@{}'.format(10)
        precision_key100 = 'Precision@{}'.format(100)
        precision_key1000 = 'Precision@{}'.format(1000)
        precision = self.intermediate_result['hit'] / (
            self.intermediate_result['total'] * self.topk)
        precision5 = self.intermediate_result5['hit'] / (
                self.intermediate_result5['total'] * 5)
        precision10 = self.intermediate_result10['hit'] / (
                self.intermediate_result10['total'] * 10)
        precision100 = self.intermediate_result100['hit'] / (
                self.intermediate_result100['total'] * 100)
        precision1000 = self.intermediate_result1000['hit'] / (
                self.intermediate_result1000['total'] * 1000)
        if 'Precision' in self.metrics:
            self.result[precision_key] = precision
            self.result[precision_key5] = precision5
            self.result[precision_key10] = precision10
            self.result[precision_key100] = precision100
            self.result[precision_key1000] = precision1000
        # recall is used to valid in the trainning, so must exit
        recall_key = 'Recall@{}'.format(self.topk)
        recall_key5 = 'Recall@{}'.format(5)
        recall_key10 = 'Recall@{}'.format(10)
        recall_key100 = 'Recall@{}'.format(100)
        recall_key1000 = 'Recall@{}'.format(1000)
        recall = self.intermediate_result['hit'] \
            / self.intermediate_result['total']
        recall5 = self.intermediate_result5['hit'] \
                 / self.intermediate_result5['total']
        recall10 = self.intermediate_result10['hit'] \
                  / self.intermediate_result10['total']
        recall100 = self.intermediate_result100['hit'] \
                  / self.intermediate_result100['total']
        recall1000 = self.intermediate_result1000['hit'] \
                  / self.intermediate_result1000['total']
        self.result[recall_key] = recall
        self.result[recall_key5] = recall5
        self.result[recall_key10] = recall10
        self.result[recall_key100] = recall100
        self.result[recall_key1000] = recall1000

        # if 'F1' in self.metrics:
        f1_key = 'F1@{}'.format(self.topk)
        self.result[f1_key] = (2 * precision * recall) / (precision +
                                                          recall)
        # if 'MRR' in self.metrics:
        mrr_key = 'MRR@{}'.format(self.topk)
        self.result[mrr_key] = self.intermediate_result['rank'] \
            / self.intermediate_result['total']

        # if 'MAP' in self.metrics:
        map_key = 'MAP@{}'.format(self.topk)
        self.result[map_key] = self.intermediate_result['rank'] \
            / self.intermediate_result['total']

        # if 'NDCG' in self.metrics:
        ndcg_key = 'NDCG@{}'.format(self.topk)
        self.result[ndcg_key] = self.intermediate_result['dcg'] \
            / self.intermediate_result['total']

        return self.result

    def save_result(self, save_path, filename=None):
        self.evaluate()
        if not os.path.exists(save_path):
            os.mkdir(save_path)
        if filename is None:
            # 使用时间戳
            filename = time.strftime(
                "%Y_%m_%d_%H_%M_%S", time.localtime(time.time()))
        print('evaluate result is ', json.dumps(self.result, indent=1))
        with open(os.path.join(save_path, '{}.json'.format(filename)), 'w') \
                as f:
            json.dump(self.result, f)

    def clear(self):
        self.result = {}
        self.intermediate_result = {
            'total': 0,
            'hit': 0,
            'rank': 0.0,
            'dcg': 0.0
        }
