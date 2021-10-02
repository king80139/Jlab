def draw_WordCloud(username,prname):
    from wordcloud import WordCloud
    import matplotlib.pyplot as plt
    from matplotlib import font_manager
    import pandas as pd
    from utils import Read_Arg_

    # stopwords = {"또는", "그리고", "매우", "그냥", "또한", "그러나", "바로", "너무", "정말", "입니다", "하는", "어떤", "에서", "이지만", "합니다", "있다",
    #               "있습니다", "있는", "있지만", "거의", "아주", "조금", "하고", "있어서", "것을", "위해", "하지만", "것입니다",
    #               "모든", "다른", "많은", "우리는", "나는", "저는", "우리가", "것이", "내가", "우리", "이는", "당신이", "우리의", "우리를", "그들은", "있고",
    #               "같은", "저희는", "곳", "곳이다", "곳입니다", "좋습니다", "좋았습니다", "좋았다", "좋았어요", "있어", "있어요", "있는데", "많이", "좋아요", "특히",
    #               "같아요", "진짜", "이다", "곳이", "경우"}


    font_fname = '/Library/Fonts/Seoulnamsan_B.otf'  # 원하는 폰트를 설정합니다.
    font_family = font_manager.FontProperties(fname=font_fname).get_name()
    plt.rcParams["font.family"] = font_family
    _, txt_file_name, plot_name = Read_Arg_("draw_WordCloud")
    if ".xlsx" in txt_file_name:
        txt_file = pd.read_excel(txt_file_name)
    elif ".csv" in txt_file_name:
        txt_file = pd.read_csv(txt_file_name)
    else:
        print("JlabMiner library Backbone Dictionary에서 draw_WordCloud의 inut_file이름을 기입해주세요")
        return


    wordcloud = WordCloud(font_path=font_fname, background_color='white',
                          width=800, height=800).generate("".join(list(txt_file["contents"])))


    plt.figure(figsize=(17,17)) #이미지 사이즈 지정
    plt.imshow(wordcloud, interpolation="catrom") #이미지의 부드럽기 정도
    plt.axis('off') #x y 축 숫자 제거

    if ".jpg" in plot_name or ".png" in plot_name or ".jpeg" in plot_name:
        plt.savefig(f"{plot_name}")
    else:
        plt.savefig(f"{plot_name}.png")
    print("사진저장완료")
    plt.show()




def draw_snplot():
    import matplotlib
    import platform
    from matplotlib import font_manager, rc
    import matplotlib.pyplot as plt
    import networkx as nx
    import pandas as pd
    from utils import Read_Sheet_, Read_Arg_


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




    matplotlib.font_manager._rebuild()

    ref_, input_, output_ = Read_Arg_(None, None, "Draw_snplot")
    try:
        Dic = Read_Sheet_(None, None, "Backbone확인받고 지울 것")
        coo = pd.read_csv(input_)
    except UnicodeDecodeError:
        Dic = Read_Sheet_(None, None, "Backbone확인받고 지울 것")
        coo = pd.read_csv(input_, encoding = "cp949")

    ## coo 로 fNl을 만들고, 이 둘을 nx에 넣어서 BC값 구해서 fNl
    # 옆에 넣어주는 거 해야함.
    tokens = set(list(coo["tag_1"]) + list(coo["tag_2"]))

    def fill_out_cooc_table_for_each_token(word, cooc_table, new_table, cluster=0):
        i = cluster + 1
        # 태그의 cooccurence 빈도를 나타내는 tag_frequency_count
        tag_frequency_count = sum(list(cooc_table[cooc_table["cluster_no"] == i].loc[
                                           cooc_table[cooc_table["cluster_no"] == i][
                                               "tag_1"] == word, "cooccurrence_count"])
                                  + list(cooc_table[cooc_table["cluster_no"] == i].loc[
                                             cooc_table[cooc_table["cluster_no"] == i][
                                                 "tag_2"] == word, "cooccurrence_count"]))
        # new_table에 tag, tag_frequency_count, cluster number순서로 차곡히 쌓아준다.
        new_table.loc[len(new_table)] = word, tag_frequency_count, i

    def calculate_bc(cooccurrence_table, fNl_table):
        import networkx as nx
        from networkx import betweenness_centrality as bc
        import pandas as pd

        graph = nx.Graph()
        relations = []
        Nodes = []

        for i, *arg in cooccurrence_table.itertuples():
            relations.append(tuple([arg[0], arg[1], {'weight': arg[2]}]))
        for i, *arg in fNl_table.itertuples():
            Nodes.append(tuple([arg[0], {'weight': arg[2]}]))
        graph.add_nodes_from(Nodes)
        graph.add_edges_from(relations)

        bc_table = pd.DataFrame(columns=["tag", "betweenness_centrality"])
        for i, elem in zip(list(bc(graph).keys()), list(bc(graph).values())):
            bc_table.loc[len(bc_table)] = i, elem
        bc_table = bc_table.sort_values(by="betweenness_centrality", ascending=False).reset_index(drop=True)

        return bc_table





    fNl = pd.DataFrame(columns=["tag", "cooccur_count", "cluster"])
    if "cluster_no" in coo.columns:
        num_cluster = coo["cluster_no"].max()
        for i in range(num_cluster):  # cluster_n_set의 개수만큼 다음의 작업을 반복한다
            for word in set(list(coo.loc[coo["cluster_no"] == i + 1, "tag_1"]) + list(
                    coo.loc[coo["cluster_no"] == i + 1, "tag_2"])):  # cluster_n_set의 tag마다
                if word in (list(coo[coo["cluster_no"] == i].tag_1) + list(coo[coo["cluster_no"] == i].tag_2)):
                    fill_out_cooc_table_for_each_token(word, coo, fNl, i)
        fNl = fNl.sort_values(by=["cluster", "cooccur_count"], ascending=[True, False]).reset_index(drop=True)
    else:
        num_cluster = 1
        coo["cluster_no"] = 1
        for word in set(list(coo["tag_1"]) + list(coo["tag_2"])):  # cluster_n_set의 tag마다
            fill_out_cooc_table_for_each_token(word, coo, fNl, 0)
        fNl = fNl.sort_values(by="cooccur_count", ascending=False).reset_index(drop=True)

    BC_Table = calculate_bc(coo, fNl)

    # 뭔가 잘못되서 임시방편으로 밑의 코드를 짭니다.
    Dic["type"] = Dic["type"] = Dic["type1"] + Dic["type2"]
    fNl["type"] = list(
        map(lambda x: list(Dic.loc[Dic["tag"] == x, "type"])[0] if x in list(Dic.tag)  else "", list(fNl.tag)))

    # b,p,l,t,o,h,f -> object
    # d,a,x -> describe

    Type_Object = []
    # Type_Attitude = [] --> 추후에 stance라는 type유형을 넣는다면 하자
    Type_Describe = []
    Type_Uncategorized = []

    def distribute_type(item):
        item_type = list(fNl.loc[fNl["tag"] == item, "type"])[0]
        if item_type == "p" or item_type == "b" or item_type == "h" or item_type == "l" or item_type == "t" or item_type == "o" or item_type == "f":
            Type_Object.append(item)
        elif item_type == "d" or item_type == "a" or item_type == "x":
            Type_Describe.append(item)
        else:
            Type_Uncategorized.append(item)
    fNl.tag.apply(distribute_type)

    tag_1_type = list(map(lambda
                              x: "type_object" if x in Type_Object else "type_describe" if x in Type_Describe else "type_uncategorized",
                          list(coo.tag_1)))
    tag_2_type = list(map(lambda
                              x: "type_object" if x in Type_Object else "type_describe" if x in Type_Describe else "type_uncategorized",
                          list(coo.tag_2)))
    coo["tag_1_type"] = tag_1_type
    coo["tag_2_type"] = tag_2_type

    def type_compare(DataFrame):
        if DataFrame["tag_1_type"] != DataFrame["tag_2_type"]:
            return "T"
    coo["type_comparison"] = coo.apply(type_compare, axis=1)

    fNl = fNl[["tag", "cooccur_count", "type"]]
    for word_in_fNl in list(set(list(fNl.tag))):
        if len(fNl[fNl["tag"] == word_in_fNl]) > 1:
            cooccur_count_sum = sum(fNl[fNl["tag"] == word_in_fNl].cooccur_count)
            fNl.loc[fNl["tag"] == word_in_fNl, "cooccur_count"] = cooccur_count_sum
    fNl = fNl[~fNl.duplicated()]

    multi_mode_Full_table = coo[coo["type_comparison"] == "T"]

    real_fNl = pd.merge(fNl, BC_Table, how="inner", on="tag")
    real_fNl = real_fNl[
        real_fNl["cooccur_count"] > (real_fNl["cooccur_count"].max()) * 0.01]  # 최소 공빈도 이상의 단어만 가져가기 (최대의 5%)
    real_fNl["O_or_D"] = real_fNl["type"].apply(
        lambda x: "D" if x in ["d", "a", "x"] else "Uncategorized" if x == "" else "O")

    multi_mode_Reduced_table = multi_mode_Full_table[(multi_mode_Full_table["tag_1"].isin(list(real_fNl.tag))) & (
        multi_mode_Full_table["tag_2"].isin(list(real_fNl.tag)))]

    threshold = .3  # 특정 수치 이상의 링크(edge)만 살리기

    multi_mode_Reduced_table["edge_threshold"] = multi_mode_Reduced_table["cooccurrence_count"].apply(
        lambda x: 0 if x / multi_mode_Reduced_table["cooccurrence_count"].max() < threshold else x)

    plt.figure(figsize=(20, 20))

    GRAPH = nx.Graph()
    Entire_relations = []
    Entire_Nodes = []

    real_fNl["edgecolor"] = real_fNl["O_or_D"].apply(
        lambda x: "lightskyblue" if x == "O" else "greenyellow" if x == "D" else "dimgray")
    for i, *arg in multi_mode_Reduced_table.itertuples():
        Entire_relations.append(tuple([arg[0], arg[1], {'weight': arg[-1]}]))
    for i, *arg in real_fNl.itertuples():
        Entire_Nodes.append(tuple([arg[0], {'weight': arg[1], 'b.c': arg[3], 'edgecolor': arg[-1]}]))
    GRAPH.add_nodes_from(Entire_Nodes)
    GRAPH.add_edges_from(Entire_relations)

    # print(Entire_relations)
    import math
    pos = nx.spring_layout(GRAPH, k=1, seed=20)
    #pos = nx.spectral_layout(GRAPH)




    nx.draw_networkx_nodes(
        GRAPH, pos, cmap="Pastel1", linewidths=5,
        edgecolors=[(n[1]['edgecolor']) for n in GRAPH.nodes(data=True)],
        node_size=[n[1]['weight'] / max(list(real_fNl.cooccur_count)) * 5000 for n in GRAPH.nodes(data=True)],
        node_color=[-1 * (n[1]['b.c']) for n in GRAPH.nodes(data=True)]
    )

    nx.draw_networkx_edges(
        GRAPH, pos, edge_color='grey', arrows=True, alpha=.6,
        width=[e[2]['weight'] / 10 for e in GRAPH.edges(data=True)]
    )

    nx.draw_networkx_labels(
        GRAPH, pos, font_size=30, font_family=font_name, font_weight='bold'
    )


    plt.axis('off')  # x y 축 숫자 제거
    if ".jpg" in output_ or ".png" in output_ or ".jpeg" in output_:
        plt.savefig(f"{output_}")
    else:
        plt.savefig(f"{output_}.png")
    plt.show()


def fitplot_3d(cooc):
    import plotly.express as px

    x = cooc[["W_1^%", "W_2^%"]].max(axis=1)
    y = cooc["W_1^%"] * cooc["W_2^%"]
    z = cooc["Fit(1|2)"]

    fig = px.scatter_3d(cooc,
                        x=x,
                        y=y,
                        z=z,
                        text=cooc["pair"],
                        opacity=.7,
                        title="fitplot 3D",
                        height=1000,
                        width=1000)
    fig.write_html("fitplot3D.html")
    fig.show()


def Draw_Map_for_Token_Match_Analysis(username, prname):
    import plotly.express as px
    from .utils import Read_Arg_, import_dataframe
    import os

    _, input_, output_ = Read_Arg_("Draw_Map_for_Token_Match_Analysis")
    if (username is None) or (prname is None) :
        cooc = import_dataframe(os.path.join(input_))
    else :
        input_directory = "/".join(username,prname)
        cooc = import_dataframe(os.path.join(input_directory, input_))
    fig = px.scatter(cooc, x="W_(2|1)^%", y="W_(1|2)^%", text="pair")
    fig.write_html(f"{output_}")
    fig.show()


def Compare_Keywords_with_Assocated_Texts(username, prname, ):
    import plotly.graph_objects as go
    import plotly.express as px
    import numpy as np
    from .utils import Read_Arg_, import_dataframe, option_finder
    import os

    _, input_, output_ = Read_Arg_("3DPlot_for_Pairs(Fit_by_Importance)")
    min_freq, max_freq = option_finder("3DPlot_for_Pairs(Fit_by_Importance)")["option_1", "option_2"]
    if (username is None) or (prname is None):
        cooc = import_dataframe(os.path.join(input_))
    else:
        input_directory = "/".join(username, prname)
        cooc = import_dataframe(os.path.join(input_directory, input_))

    cooc = cooc[
            (cooc["cooccurrence_count"] >= min_freq*cooc["cooccurrence_count"].max())&
            (cooc["cooccurrence_count"] <= max_freq*cooc["cooccurrence_count"].max())
            ]
    # x = cooc[["W_1^%","W_2^%"]].max(axis=1)
    # y = cooc["W_1^%"]*cooc["W_2^%"]
    z = np.log(cooc["Fit(1|2)"])

    fig = px.scatter_3d(cooc,
                        x="W_1^%",
                        y="W_2^%",
                        z=z,
                        text=cooc["pair"],
                        opacity=.7,
                        title="fitplot 3D",
                        height=1000,
                        width=1000)

    xaxis_min = cooc["W_1^%"].min()
    xaxis_max = cooc["W_1^%"].max()
    yaxis_min = cooc["W_2^%"].min()
    yaxis_max = cooc["W_2^%"].max()
    dict_z = {"x": [xaxis_min, xaxis_max, xaxis_max, xaxis_max, xaxis_max, xaxis_min, xaxis_min, xaxis_min],
              "y": [yaxis_min, yaxis_min, yaxis_min, yaxis_max, yaxis_max, yaxis_max, yaxis_max, yaxis_min],
              "z": [0] * 8}

    fig.add_trace(go.Scatter3d(x=dict_z["x"],
                               y=dict_z["y"],
                               z=dict_z["z"],
                               mode="lines",
                               line=dict(width=10,
                                         color="rgb(000, 000, 000)"),
                               surfaceaxis=2,
                               surfacecolor="rgb(204, 204, 153)",
                               opacity=.5))
    fig.write_html(f"{output_}")
    fig.show()



def draw_subjDesc_plot(username, prname):
    import pandas as pd
    import matplotlib
    import platform
    from matplotlib import font_manager, rc
    from utils import Read_Sheet_, Read_Arg_
    import matplotlib.pyplot as plt

    import networkx as nx

    plt.rcParams['axes.unicode_minus'] = False
    # % matplotlib inline
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
            raise Exception('적절한 한글용 폰트의 경로가 설정되지 않았습니다. ')
    except Exception as e:  # 예외가 발생했을 때 실행됨
        print('예외가 발생했습니다.', e)

    matplotlib.font_manager._rebuild()

    ref_, input_, output_ = Read_Arg_(None, None, "draw_subjDesc_plot")
    try:
        Dic = Read_Sheet_(None, None, "Backbone확인받고 지울 것")
        coo = pd.read_csv(input_)
    except UnicodeDecodeError:
        Dic = Read_Sheet_(None, None, "Backbone확인받고 지울 것")
        coo = pd.read_csv(input_, encoding="cp949")

    wordList = list(set(coo["tag_1"].append(coo["tag_2"])))
    wordDic = {}
    for w in wordList:
        print(w)
        if len(Dic.loc[(Dic["tag"] == w) & (Dic["type1"] == "b"), "type1"]) == 0:
            brand = ""
        elif len(Dic.loc[(Dic["tag"] == w) & (Dic["type1"] == "b"), "type1"]) != 0:
            brand = w
        else:
            pass

        if len(Dic[(Dic["tag"] == w) & (Dic["product_attribute"] != "")]["product_attribute"].dropna()) == 0:
            prodAtt = ""
        elif len(Dic[(Dic["tag"] == w) & (Dic["product_attribute"] != "")]["product_attribute"].dropna()) != 0:
            prodAtt = Dic[(Dic["tag"] == w) & (Dic["product_attribute"] != "")]["product_attribute"].tolist()[0]
        else:
            pass

        if len(Dic[(Dic["tag"] == w) & (Dic["valence"] != "")]["valence"].dropna()) == 0:
            valence = ""
        elif len(Dic[(Dic["tag"] == w) & (Dic["valence"] != "")]["valence"].dropna()) != 0:
            prodAtt = Dic[(Dic["tag"] == w) & (Dic["valence"] != "")]["valence"].tolist()[0]
        else:
            pass

        wordDic[w] = [brand, prodAtt, valence]

    coo["tag_1_brand"] = coo["tag_1"].apply(lambda x : wordDic[x][0])
    coo["tag_1_attrib"] = coo["tag_1"].apply(lambda x: wordDic[x][1])
    coo["tag_1_valence"] = coo["tag_1"].apply(lambda x: wordDic[x][2])
    coo["tag_2_brand"] = coo["tag_2"].apply(lambda x: wordDic[x][0])
    coo["tag_2_attrib"] = coo["tag_2"].apply(lambda x: wordDic[x][1])
    coo["tag_2_valence"] = coo["tag_2"].apply(lambda x: wordDic[x][2])
    #
    # coo = coo[
    #         ((coo["tag_1_attrib"] is not None) and (coo["tag_2_brand"] is not None)) or
    #         ((coo["tag_1_brand"] is not None) and (coo["tag_2_attrib"] is not None))
    # ]


    return coo


def SNA_3Gram(username, prname, isind=0, min_thresh_rate=0.01, nodesize_var=500, edgesize_var=1000, k=1, seed=20):
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
    # % matplotlib inline
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
    # Freq_100_tag = list(Freq_100.tag)

    # tags_labeled = Freq_100.join(Read_Sheet_(prname, username, ref)[["tag","type1","type2","valence"]], on = "tag", how = "left")
    tags_labeled = pd.merge(Freq_100, Read_Sheet_(prname, username, ref)[["tag", "type1", "type2", "valence"]],
                            on="tag", how="left")
    tags_labeled["type"] = tags_labeled["type1"] + tags_labeled["type2"]
    tags_labeled = tags_labeled[tags_labeled["type"].isin(list(options.values()))][
        ["tag", "count", "type", "valence"]].drop_duplicates(keep="first")
    items = [list(tags_labeled[tags_labeled["type"] == options["option_1"]]["tag"]),
             list(tags_labeled[tags_labeled["type"] == options["option_2"]]["tag"]),
             list(tags_labeled[tags_labeled["type"] == options["option_3"]]["tag"]),
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
        cooccur_subdict["level1&2_cooccurence"] = len(
            Message_Df[Message_Df["contents"].str.contains("&".join([item[0], item[1]]), na=False)])
        cooccur_subdict["level1&2&3_cooccurence"] = len(
            Message_Df[Message_Df["contents"].str.contains("&".join([item[0], item[1], item[2]]), na=False)])
        cooccur_dict[f"combi_{i + 1}"] = cooccur_subdict
        cooccur_subdict = {}
        print(cooccur_dict)

    graph = nx.Graph()
    nodes = []
    edges = []

    cooccur_table = pd.DataFrame(cooccur_dict).transpose()
    max_count = max(
        list(cooccur_table.level1_count) + list(cooccur_table.level2_count) + list(cooccur_table.level3_count))

    for i, *arg in cooccur_table.itertuples():
        nodes.append(tuple([arg[0], {'weight': arg[1], 'type': arg[2], 'polarity': arg[3]}]))  # 첫단어와 그 메타 정보
        nodes.append(tuple([arg[4], {'weight': arg[5], 'type': arg[6], 'polarity': arg[7]}]))  # 두 번째 단어와 그 메타 정보
        nodes.append(tuple([arg[8], {'weight': arg[9], 'type': arg[10], 'polarity': arg[11]}]))  # 세 번째 단어와 그 메타 정보
    for i, *arg in cooccur_table.itertuples():
        edges.append(tuple([arg[0], arg[4], {'weight': arg[12]}]))  # 첫단어 두 번 째 단어의 연관과 그 강도 level1&2_cooccurence
        edges.append(tuple(
            [arg[4], arg[8], {'weight': arg[13]}]))  # 두번째 단어와 세번째 단어의 연관과 그 강도 : 세 단어들의 공빈도 level1&2&3_cooccurence

    graph.add_nodes_from(nodes)
    graph.add_edges_from(edges)

    pos = nx.spring_layout(graph, k=k, seed=seed)

    nx.draw_networkx_nodes(
        graph, pos, cmap="Pastel1", linewidths=5,
        # edgecolors=[(n[1]['type']) for n in graph.nodes(data=True)],
        node_size=[n[1]['weight'] / max_count * nodesize_var for n in graph.nodes(data=True)],
        # node_color=[-1 * ((n[1]['polarity']) if (n[1]['polarity']) != "" else 0) for n in graph.nodes(data=True)]
    )

    nx.draw_networkx_edges(
        graph, pos, edge_color='black', arrows=True, alpha=.6,
        width=[e[2]['weight'] * edgesize_var for e in graph.edges(data=True)]
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



__all__ = ['draw_snplot', 'draw_WordCloud', 'Compare_Keywords_with_Assocated_Texts', 'Draw_Map_for_Token_Match_Analysis', 'draw_subjDesc_plot', 'SNA_3Gram']



