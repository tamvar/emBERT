#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Evaluation / prediction functions."""

from itertools import takewhile
from typing import List

import torch
from torch import nn
import torch.nn.functional as F

from .data_wrapper import DataWrapper


def predict(model: nn.Module, wrapper: DataWrapper) -> List[List[str]]:
    """Predicts the labels for all sentences in _wrapper_."""
    sep_id = len(wrapper.get_labels())  # [SEP] is always the last label

    inputs = []
    y_pred = []
    model.eval()
    for (
        input_ids, input_mask, segment_ids, label_ids, valid_ids, l_mask
    ) in wrapper:
        with torch.no_grad():
            logits = model(input_ids, segment_ids, input_mask, labels=None,
                           valid_ids=valid_ids, attention_mask_label=l_mask)[0]
        logits = torch.argmax(F.log_softmax(logits, dim=2), dim=2)
        # batch_size x seq_len
        logits = logits.detach().cpu().numpy()[:, 1:]
        input_ids = input_ids.detach().cpu().numpy()[:, 1:]

        y_pred += [
            [wrapper.id_to_label(label_id)
             for label_id in takewhile(lambda l: l != sep_id, seq)]
            for seq in logits
        ]
        inputs += [wrapper.tokenizer.convert_ids_to_tokens(seq_ids) for seq_ids in input_ids]

    return y_pred
