
def SNA_3Gram(username, prname, isind = 0, min_thresh_rate = 0.01,  nodesize_var = 500, edgesize_var = 1000 , k=1, seed = 20):
    from Jlab_Text_Cleaning_Functions import Frequency_Analysis
    import pandas as pd
    from utils import Read_Arg_, Read_Sheet_, option_finder, import_dataframe, export_dataframe
    from matplotlib import font_manager, rc
    import matplotlib.pyplot as plt
    from itertools import product
    import platform
    import networkx as nx
    from tqdm import tqdm

    plt.rcParams['axes.unicode_minus'] = False
    #% matplotlib inline
    plt.figure(figsize=(30, 30))

    try:
        # 한글 폰트 설정을 위한 코드블럭입니다.
        if platform.system() == 'Darwin':  # 맥os 사용자의 경우에
            plt.style.use('seaborn-darkgrid')
            font_name = "AppleGothic"
            rc('font', family=font_name)
        elif platform.system() == 'Windows':  # 윈도우 사용자의 경우에
            path = 'c:/Windows/Fonts/malgun.ttf'
            font_name = font_manager.FontProperties(fname=path).get_name()
            plt.style.use('seaborn-darkgrid')  # https://python-graph-gallery.com/199-matplotlib-style-sheets/
            rc('font', family=font_name)
        elif platform.system() == "Linux":  # 코랩에서 사용할 경우
            path = '/usr/share/fonts/truetype/nanum/NanumBarunGothic.ttf'
            font_name = font_manager.FontProperties(fname=path).get_name()
            plt.style.use('seaborn-darkgrid')
            plt.rc('font', family=font_name)
        else:
            font_name = ""
            raise Exception('적절한 한글용 폰트의 경로가 설정되지 않았습니다. draw_snplot.py파일의 15~28번째 줄을 참고하십시오.')
    except Exception as e:  # 예외가 발생했을 때 실행됨
        print('예외가 발생했습니다.', e)

    if prname is not None:
        ind = 1  # 독립적으로 쓰이는 경우, Backbone사용
    else:
        ind = 0  # 다른 함수 내에서 사용될 경우, username에 분석할 text데이터를 넣는다.

    ref, input_, output_ = Read_Arg_(prname, username, "SNA_3Gram")
    options = option_finder(prname, username, "SNA_3Gram")

    Message_Df = import_dataframe(input_)

    Freq_df = Frequency_Analysis(Message_Df, prname)  # 검색어 포함 할 때
    Freq_100 = Freq_df[Freq_df["count"] >= Freq_df["count"].max() * min_thresh_rate]  # 원래 ref라는 변수로 비율을 가져와야 하느데...
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
        item = cooccur_list_1[i]
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
        cooccur_subdict["level1&2_cooccurence"] = len(Message_Df[Message_Df["contents"].str.contains("&".join([item[0], item[1]]), na = False)])
        cooccur_subdict["level1&2&3_cooccurence"] = len(Message_Df[Message_Df["contents"].str.contains("&".join([item[0], item[1], item[2]]), na = False)])
        cooccur_dict[f"combi_{i+1}"] = cooccur_subdict
        cooccur_subdict = {}
        print(cooccur_dict)

    graph = nx.Graph()
    nodes = []
    edges = []

    cooccur_table = pd.DataFrame(cooccur_dict).transpose()
    max_count = max(list(cooccur_table.level1_count)+list(cooccur_table.level2_count)+list(cooccur_table.level3_count))

    for i, *arg in cooccur_table.itertuples():
        nodes.append(tuple([arg[0], {'weight': arg[1], 'type': arg[2], 'polarity': arg[3]}])) # 첫단어와 그 메타 정보
        nodes.append(tuple([arg[4], {'weight': arg[5], 'type': arg[6], 'polarity': arg[7]}])) # 두 번째 단어와 그 메타 정보
        nodes.append(tuple([arg[8], {'weight': arg[9], 'type': arg[10], 'polarity': arg[11]}])) # 세 번째 단어와 그 메타 정보
    for i, *arg in cooccur_table.itertuples():
        edges.append(tuple([arg[0], arg[4], {'weight': arg[12]}]))   # 첫단어 두 번 째 단어의 연관과 그 강도 level1&2_cooccurence
        edges.append(tuple([arg[4], arg[8], {'weight': arg[13]}]))   # 두번째 단어와 세번째 단어의 연관과 그 강도 : 세 단어들의 공빈도 level1&2&3_cooccurence

    graph.add_nodes_from(nodes)
    graph.add_edges_from(edges)


    pos = nx.spring_layout(graph, k=k, seed=seed)

    nx.draw_networkx_nodes(
        graph, pos, cmap="Pastel1", linewidths=5,
        #edgecolors=[(n[1]['type']) for n in graph.nodes(data=True)],
        node_size=[n[1]['weight'] / max_count * nodesize_var for n in graph.nodes(data=True)],
        #node_color=[-1 * ((n[1]['polarity']) if (n[1]['polarity']) != "" else 0) for n in graph.nodes(data=True)]
    )

    nx.draw_networkx_edges(
        graph, pos, edge_color='black', arrows=True, alpha=.6,
        width=[e[2]['weight']*edgesize_var for e in graph.edges(data=True)]
    )

    nx.draw_networkx_labels(
        graph, pos, font_size=30, font_family=font_name, font_weight='bold'
    )


    plt.axis('off')  # x y 축 숫자 제거
    if ".jpg" in output_ or ".png" in output_ or ".jpeg" in output_:
        plt.savefig(f"{output_}")
    else:
        plt.savefig(f"{output_}.png")
    plt.show()


# print(input_)
# print(output_)
# print(tags_labeled)
# print(options)
# print(cooccur_list_1)
# print(cooccur_dict)
#
# pd.DataFrame(cooccur_dict)
