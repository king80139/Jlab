def Calculate_BD(brand_list, Axes = ["a","p","i"], input_directory = ""):
    '''
    :param brand_list: 분석할 브랜드를 담은 리스트. 예: brand_list = ["스타벅스", "이디야", "블루보틀", "빽다방", "투썸플레이스", "폴바셋", "공차"]
    :param input_directory:
    :return:
    '''
    from .utils import Read_Arg_, Read_Sheet_, import_dataframe, export_dataframe
    import re
    import os
    import pandas as pd
    from .Jlab_Text_Cleaning_Functions import make_cotable
    from itertools import combinations

    ref, input_, output_ = Read_Arg_("Calculate_BD")

    ws = pd.DataFrame(Read_Sheet_("JDic_Backbone_Korean"))[[
        "tag", "type1", "type2", "valence", "product_attribute"]
    ][4:]

    att_set = pd.DataFrame(columns = ["tag", "product_attribute"])
    for axis in Axes:
        att_set = att_set.append(ws[ws["product_attribute"] == axis][["tag","product_attribute"]])
    for brand in brand_list:
        att_set = att_set.append(ws[ws["tag"] == brand][["tag","product_attribute"]])

    att_set = att_set[~att_set["tag"].duplicated()]

    input_name = os.path.join(input_directory, input_)
    Message_Df = import_dataframe(input_name)

    ref_name = os.path.join(input_directory, ref)
    Freq = import_dataframe(ref_name)

    classified = pd.merge(Freq, att_set, on="tag", how="inner").sort_values(by="product_attribute")

    CoTable = make_cotable(classified["tag"].tolist(), Message_Df)

    CoTable_stacked = CoTable.loc[brand_list,:].stack().reset_index()  # 각 브랜드와 기술노드들의 공빈도를 보기 위해 브랜드들만 row로 삼아주기
    CoTable_stacked.rename(columns={'level_0': 'tag_1', 'level_1': 'tag_2', 0: 'cooccurence_count'}, inplace=True)
    CoTable_stacked.sort_values(by='cooccurence_count', ascending=False, inplace=True)
    CoTable_stacked = CoTable_stacked[CoTable_stacked["cooccurence_count"] > 0]
    CoTable_stacked.reset_index(drop=True, inplace=True)

    Dis_1 = pd.merge(CoTable_stacked, classified, left_on="tag_2", right_on="tag", how="inner").drop("tag", axis=1)
    Dis_1 = Dis_1[~ (Dis_1["product_attribute"] == "")]
    Dis_1 = Dis_1.groupby(["tag_1", "product_attribute", "tag_2", "cooccurence_count"]).sum().reset_index()

    # "한 기술노드가 포함된 세트에서 그 기술노드의 비중(표준비중)"을 구하기 위해 필요한 특정 기술노드의 총 공빈도를 계산하기 위해 테이블을 만들어준 후
    DIS = Dis_1.copy().groupby(["tag_1", "product_attribute"])["cooccurence_count"].sum().reset_index()
    DIS = pd.merge(DIS, DIS.groupby(["tag_1"])["cooccurence_count"].sum().reset_index(name="cooc_sum"),
                     on="tag_1", how="inner")
    DIS["k_set_weight"] = DIS["cooccurence_count"] / DIS["cooc_sum"]

    # 위 두 테이블을 병합시켜 cooccur_ratio라는 컬럼에 그 값을 계산해줍니다.
    Dis_1 = pd.merge(Dis_1, DIS, on=["tag_1", "product_attribute"], how="outer")
    Dis_1.columns = ["tag_1", "product_attribute", "tag_2", "tag_1, tag_2 cooccur", "tag_2_count", "tag_1_PA_cooccur",
                     "cooccur_sum_by_k", "k_set_weight"]
    Dis_1["cooccur_ratio"] = Dis_1["tag_1, tag_2 cooccur"] / Dis_1["tag_1_PA_cooccur"]

    # Dissimmilarity를 기준으로 3d_plot을 그리기 위한 table을 만듭니다.
    table_for_3dplot = pd.DataFrame(columns=Axes, index=brand_list)
    weight_table = table_for_3dplot.copy()

    table = Dis_1.groupby(["tag_1","product_attribute"])["tag_1_PA_cooccur"].sum().reset_index(name = "total")
    cooc_total = pd.DataFrame(table.copy().groupby("tag_1")["total"].sum()).reset_index()
    print(table)
    table_ = pd.merge(table, cooc_total, on = "tag_1", how = "inner")
    table_["weight_ratio"] = table_["total_x"] / table_["total_y"]
    print(table_)


    for brand in brand_list:
       weight_table.loc[brand] = table_[table_["tag_1"]==brand]["weight_ratio"].tolist()
    table_for_3dplot = weight_table / weight_table.median(axis = 0)
    table_for_3dplot.to_csv(os.path.join(input_directory, output_.split(",")[4]), encoding="cp949")

    BrSets = []
    for A, B in combinations(brand_list, 2):
        BrSets.append([A, B])

    # 브랜드들을 비교한 기술노드들의 유일값을 comp_tag 변수에 담아주고,
    comp_tag = Dis_1["tag_2"].unique()

    # Brand_Distance table을 새로 정해줍니다.
    BrDis_df = pd.DataFrame(
        columns=["brand_1", "brand_2", "desc_tag", "product_attribute", "brand_1_ratio", "brand_2_ratio",
                 "BrDis_k_set(A/B)"])
    k_set_BD = pd.DataFrame(columns=["brand_1", "brand_2", "product_attribute", "BrDis_k_set(A/B)"])

    # 조합마다 각 tag의 ratio들과 그 brand_1 ratio를 brane_2 ratio로 나눈 Brand Distance lv1을 구해준 후, Brand_Distance table에 차례대로 삽입해줍니다.
    print(Dis_1)
    print(BrSets)
    for i in range(len(BrSets)):
        tag_A, tag_B = BrSets[i]
        for tag in comp_tag:
            tag_A_ratio = Dis_1.loc[(Dis_1["tag_1"] == tag_A) & (Dis_1["tag_2"] == tag), "cooccur_ratio"].values[0]
            tag_B_ratio = Dis_1.loc[(Dis_1["tag_1"] == tag_B) & (Dis_1["tag_2"] == tag), "cooccur_ratio"].values[0]
            tag_att = Dis_1.loc[(Dis_1["tag_2"] == tag), "product_attribute"].values[0]
            BrDis_k_set = Dis_1.loc[(Dis_1["tag_1"] == tag_A) & (Dis_1["tag_2"] == tag), "k_set_weight"].values[0] / \
                          Dis_1.loc[(Dis_1["tag_1"] == tag_B) & (Dis_1["tag_2"] == tag), "k_set_weight"].values[0]
            BrDis_df.loc[len(BrDis_df)] = tag_A, tag_B, tag, tag_att, tag_A_ratio, tag_B_ratio, BrDis_k_set

            k_set_BD.loc[len(k_set_BD)] = tag_A, tag_B, tag_att, BrDis_k_set

    k_set_BD = k_set_BD[~k_set_BD.duplicated()]
    BrDis_df["BrDis_k_node"] = BrDis_df["brand_1_ratio"] / BrDis_df["brand_2_ratio"]

    # OVR BrandDistance를 구하기 위한 속성 k의 weight를 구하고, k_set BrandDistance에 곱한바를 전부 합해 OVR BrandDistance를 구한다.
    total_k_freq = classified[classified["product_attribute"] != ""]["count"].sum()
    weight_1 = classified[classified["product_attribute"] == Axes[0]]["count"].sum() / total_k_freq
    weight_2 = classified[classified["product_attribute"] == Axes[1]]["count"].sum() / total_k_freq
    weight_3 = classified[classified["product_attribute"] == Axes[2]]["count"].sum() / total_k_freq

    OVR_BD = pd.DataFrame(columns=["brand_1", "brand_2", "OVR_BD"])
    for i in range(len(BrSets)):
        tag_A, tag_B = BrSets[i]
        BD_for_1 = BrDis_df[(BrDis_df["brand_1"] == tag_A) & (BrDis_df["brand_2"] == tag_B) & (
                    BrDis_df["product_attribute"] == Axes[0])]["BrDis_k_set(A/B)"].values[0]
        BD_for_2 = BrDis_df[(BrDis_df["brand_1"] == tag_A) & (BrDis_df["brand_2"] == tag_B) & (
                    BrDis_df["product_attribute"] == Axes[1])]["BrDis_k_set(A/B)"].values[0]
        BD_for_3 = BrDis_df[(BrDis_df["brand_1"] == tag_A) & (BrDis_df["brand_2"] == tag_B) & (
                    BrDis_df["product_attribute"] == Axes[2])]["BrDis_k_set(A/B)"].values[0]
        ovr_BD = (weight_1 * BD_for_1) + (weight_2 * BD_for_2) + (weight_3 * BD_for_3)
        OVR_BD.loc[len(OVR_BD)] = tag_A, tag_B, ovr_BD

    BrDis_df = pd.merge(BrDis_df, OVR_BD, on=["brand_1", "brand_2"], how="inner")
    BrDis_df = BrDis_df.sort_values(by=["desc_tag", "BrDis_k_node"], ascending=False).reset_index(drop=True)

    export_dataframe(Dis_1, os.path.join(input_directory, output_.split(",")[0]))
    export_dataframe(OVR_BD, os.path.join(input_directory, output_.split(",")[1]))
    export_dataframe(k_set_BD, os.path.join(input_directory, output_.split(",")[2]))
    export_dataframe(BrDis_df, os.path.join(input_directory, output_.split(",")[3]))
    table_for_3dplot.to_csv(os.path.join(input_directory, output_.split(",")[4]), encoding = "cp949")
    #export_dataframe(table_for_3dplot, os.path.join(input_directory, output_.split(",")[4]))

    return Dis_1, OVR_BD, k_set_BD, BrDis_df, table_for_3dplot