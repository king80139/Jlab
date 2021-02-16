def draw_WordCloud():
    from wordcloud import WordCloud
    import matplotlib.pyplot as plt
    from matplotlib import font_manager
    import pandas as pd
    from .utils import Read_Arg_

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
    from .utils import Read_Sheet_, Read_Arg_


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

    ref_, input_, output_ = Read_Arg_("draw_snplot")
    try:
        Dic = Read_Sheet_("JDic_Backbone_Korean")
        coo = pd.read_csv(input_)
    except UnicodeDecodeError:
        Dic = Read_Sheet_("JDic_Backbone_Korean")
        coo = pd.read_csv(input_, encoding = "cp949")

    ## coo 로 fNl을 만들고, 이 둘을 nx에 넣어서 BC값 구해서 fNl옆에 넣어주는 거 해야함.
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
        real_fNl["cooccur_count"] > (real_fNl["cooccur_count"].max()) * 0.05]  # 최소 공빈도 이상의 단어만 가져가기 (최대의 5%)
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
    pos = nx.spring_layout(GRAPH, k=100 / math.sqrt(GRAPH.order()), seed=20)



    nx.draw_networkx_nodes(
        GRAPH, pos, cmap="Reds", linewidths=5,
        edgecolors=[(n[1]['edgecolor']) for n in GRAPH.nodes(data=True)],
        node_size=[n[1]['weight'] / max(list(real_fNl.cooccur_count)) * 5000 for n in GRAPH.nodes(data=True)],
        node_color=[-1 * (n[1]['b.c']) for n in GRAPH.nodes(data=True)]
    )

    nx.draw_networkx_edges(
        GRAPH, pos, edge_color='grey', arrows=True, alpha=.6,
        width=[e[2]['weight'] / 100 for e in GRAPH.edges(data=True)]
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


__all__ = ['draw_snplot', 'draw_WordCloud']
