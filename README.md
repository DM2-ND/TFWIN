# TFWIN

Source code and dataset of TheWebConf 2019 paper: "A Novel Unsupervised Approach for Precise Temporal Slot Filling from Incomplete and Noisy Temporal Contexts"

Authors: Xueying Wang (xwang41@nd.edu), Haiqiao Zhang, Qi Li, Yiyu Shi, Meng Jiang

If you use the code/data please cite this paper: 

```
@inproceedings{wang2019novel,
  title={A Novel Unsupervised Approach for Precise Temporal Slot Filling from Incomplete and Noisy Temporal Contexts},
  author={Wang, Xueying and Zhang, Haiqiao and Li, Qi and Shi, Yiyu and Jiang, Meng},
  booktitle={Proceedings of TheWebConf 2019},
  year={2019}
}
```

# Overview

In this work, we proposed an unsupervised approach of two modules that mutually enhance each other: one is a reliability estimator on fact extractors conditionally to the temporal contexts; the other is a fact trustworthiness estimator based on the extractor’s reliability. The iterative learning process reduces the noise of the extractions. 

# Data
This folder "data" contains 4 structured datasets for termpoal facts extraction. 

data_post_CP: country's president data with post time signal    
data_post_SP: sport's player data with post time signal     
data_text_CP: country's president data with text time signal    
data_text_CP: sport's player data with text time signal    

Format of these four datasets are same, for each line:  
```
RANKPATTERN \t PATTERN \t ENTITYPOS \t VALUEPOS \t RANKENTITYVALUETM \t ENTITY \t VALUE \t TM \t COUNT
```

Besides, ground truth for "country's president" is collected in "groundtruth_president". 

# Codes 
The source codes of our models are in "tfwin.py", run with python 2.7

