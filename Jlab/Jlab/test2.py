from Jlab_Text_Cleaning_Functions import Frequency_Analysis
import pandas as pd
from utils import Read_Arg_, Read_Sheet_, option_finder, import_dataframe, export_dataframe
from itertools import product
from tqdm import tqdm

prname = None
username = None

if prname is not None:
    ind = 1  # 독립적으로 쓰이는 경우, Backbone사용
else:
    ind = 0  # 다른 함수 내에서 사용될 경우, username에 분석할 text데이터를 넣는다.

ref, input_, output_ = Read_Arg_(prname, username, "SNA_3Gram")
options = option_finder(prname, username, "SNA_3Gram")

Message_Df = import_dataframe(input_)

Freq_df = Frequency_Analysis(Message_Df, prname)  # 검색어 포함 할 때
Freq_100 = Freq_df[Freq_df["count"] >= Freq_df["count"].max() * 0.0001]  # 원래 ref라는 변수로 비율을 가져와야 하느데...
#Freq_100_tag = list(Freq_100.tag)

#tags_labeled = Freq_100.join(Read_Sheet_(prname, username, ref)[["tag","type1","type2","valence"]], on = "tag", how = "left")
tags_labeled = pd.merge(Freq_100, Read_Sheet_(prname, username, ref)[["tag","type1","type2","valence"]], on = "tag", how = "left")
tags_labeled["type"] = tags_labeled["type1"] + tags_labeled["type2"]
tags_labeled = tags_labeled[tags_labeled["type"].isin(list(options.values()))][["tag","count","type","valence"]].drop_duplicates(keep = "first")
items = [list(tags_labeled[tags_labeled["type"]==options["option_1"]]["tag"]),
            list(tags_labeled[tags_labeled["type"]==options["option_2"]]["tag"]),
            list(tags_labeled[tags_labeled["type"]==options["option_3"]]["tag"]),
        ]
cooccur_list_1 = list(product(*items))

cooccur_dict = {}
cooccur_subdict = {}
for i in range(len(cooccur_list_1)):
    for item in cooccur_list_1:
        print(item)
        cooccur_subdict["level1_tag"] = item[0]
        cooccur_subdict["level1_count"] = tags_labeled[tags_labeled["tag"] == item[0]]["count"].values[0]
        cooccur_subdict["level1_type"] = tags_labeled[tags_labeled["tag"] == item[0]]["type"].values[0]
        cooccur_subdict["level1_polarity"] = tags_labeled[tags_labeled["tag"] == item[0]]["valence"].values[0]
        cooccur_subdict["level2_tag"] = item[1]
        cooccur_subdict["level2_count"] = tags_labeled[tags_labeled["tag"] == item[1]]["count"].values[0]
        cooccur_subdict["level2_type"] = tags_labeled[tags_labeled["tag"] == item[1]]["type"].values[0]
        cooccur_subdict["level2_polarity"] = tags_labeled[tags_labeled["tag"] == item[1]]["valence"].values[0]
        cooccur_subdict["level3_tag"] = item[2]
        cooccur_subdict["level3_count"] = tags_labeled[tags_labeled["tag"] == item[2]]["count"].values[0]
        cooccur_subdict["level3_type"] = tags_labeled[tags_labeled["tag"] == item[2]]["type"].values[0]
        cooccur_subdict["level3_polarity"] = tags_labeled[tags_labeled["tag"] == item[2]]["valence"].values[0]
        cooccur_subdict["level1&2_cooccurence"] = len(Message_Df[Message_Df["contents"].str.contains("&".join([item[0], item[1]]))])
        cooccur_subdict["level1&2&3_cooccurence"] = len(Message_Df[Message_Df["contents"].str.contains("&".join([item[0], item[1], item[2]]))])
    cooccur_dict[f"combi_{i}"] = cooccur_subdict

print(input_)
print(output_)
print(tags_labeled)
print(options)
print(cooccur_list_1)
print(cooccur_dict)

pd.DataFrame(cooccur_dict)
